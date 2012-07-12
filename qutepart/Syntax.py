"""Kate syntax definition parser and representation
Read http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/ 
if you want to understand something
"""

import os.path
import re
import xml.etree.ElementTree

class AbstractRule:
    """Base class for rule classes
    """
    def __init__(self, context, xmlElement):
        """Parse XML definition
        """
        self.context = context

        for key, value in xmlElement.items():
            setattr(self, key, value)

    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\t\tRule %s\n' % self.__class__.__name__
        for name, value in vars(self).iteritems():
            res += '\t\t\t%s: %s\n' % (name, value)
        return res
    
    def findMatch(self, text):
        """Try to find themselves in the text.
        Returns matched length, or None if not matched
        """
        raise NotImplementedFault()


class DetectChar(AbstractRule):
    def findMatch(self, text):
        if text[0] == self.char:
            return 1
        return None

class Detect2Chars(AbstractRule):
    pass
class AnyChar(AbstractRule):
    pass
class StringDetect(AbstractRule):
    pass
class WordDetect(AbstractRule):
    pass


class RegExpr(AbstractRule):
    """TODO if regexp starts with ^ - match only column 0
    TODO support "minimal" flag
    """
    def __init__(self, *args):
        self.insensitive = False  # default value
        
        AbstractRule.__init__(self, *args)
        
        flags = 0
        if self.insensitive:
            flags = re.IGNORECASE
        
        self._regExp = re.compile(self.String)

    def findMatch(self, text):
        match = self._regExp.match(text)
        if match is not None:
            return len(match.group(0))


class keyword(AbstractRule):
    def findMatch(self, text):
        if not self.context.syntax.casesensetive:
            text = text.lower()
        
        for word in self.context.syntax.lists[self.String]:
            if text.startswith(word):
                return len(word)
        
        return None

class Int(AbstractRule):
    pass
class Float(AbstractRule):
    pass
class HlCOct(AbstractRule):
    pass
class HlCHex(AbstractRule):
    pass
class HlCStringChar(AbstractRule):
    pass
class HlCChar(AbstractRule):
    pass
class RangeDetect(AbstractRule):
    pass
class LineContinue(AbstractRule):
    pass
class IncludeRules(AbstractRule):
    pass
class DetectSpaces(AbstractRule):
    pass
class DetectIdentifier(AbstractRule):
    pass

_ruleClasses = (DetectChar, Detect2Chars, AnyChar, StringDetect, WordDetect, RegExpr,
                keyword, Int, Float, HlCOct, HlCHex, HlCStringChar, HlCChar, RangeDetect,
                LineContinue, IncludeRules, DetectSpaces, DetectIdentifier)


class Context:
    def __init__(self, syntax, xmlElement):
        """Construct context from XML element
        """
        self.syntax = syntax

        # Default values for optional attributes
        self.lineBeginContext = '#stay'
        self.fallthrough = False
        self.dynamic = False
        self.fallthroughContext = ''
        
        # Read attributes, overwrite defaults, if attribute is set
        for key, value in xmlElement.items():
            setattr(self, key, value)
        
        self.rules = []

        ruleClassDict = {}
        for ruleClass in _ruleClasses:
            ruleClassDict[ruleClass.__name__] = ruleClass
        
        for ruleElement in xmlElement.getchildren():
            if not ruleElement.tag in ruleClassDict:
                raise ValueError("Not supported rule '%s'" % ruleElement.tag)
            rule = ruleClassDict[ruleElement.tag](self, ruleElement)
            self.rules.append(rule)
    
    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\tContext %s\n' % self.name
        for name, value in vars(self).iteritems():
            if name != 'rules':
                res += '\t\t%s: %s\n' % (name, value)
        
        for rule in self.rules:
            res += str(rule)
        return res


class Syntax:
    """Syntax file parser and container
    
    Public attributes:
        lists - Keyword lists as dictionary "list name" : "list value"
        contexts - Context list as dictionary "context name" : context
        defaultContext - Default context object
        deliminatorSet - Set of deliminator characters
        caseSensetive - Keywords are case sensetive. Global flag, every keyword might have own value
    """
    
    _DEFAULT_DELIMINATOR = " \t.():!+,-<=>%&*/;?[]^{|}~\\"

    def __init__(self, fileName):
        """Parse XML definition
        """
        # Default parameters
        self.deliminatorSet = set(Syntax._DEFAULT_DELIMINATOR)
        self.casesensitive = True
        
        modulePath = os.path.dirname(__file__)
        dataFilePath = os.path.join(modulePath, "syntax", fileName)
        with open(dataFilePath, 'r') as dataFile:
            root = xml.etree.ElementTree.parse(dataFile).getroot()
        
        # read attributes
        for key, value in root.items():
            setattr(self, key, value)
        
        hlgElement = root.find('highlighting')
        
        # parse lists
        self.lists = {}  # list name: list
        for listElement in hlgElement.findall('list'):
            items = [item.text \
                        for item in listElement.findall('item')]
            self.lists[listElement.attrib['name']] = items
        
        # Make all keywords lowercase, if syntax is not case sensetive
        if not self.casesensitive:
            for keywordList in self.lists.items():
                for index, keyword in enumerate(keywordList):
                    keywordList[index] = keyword.lower()
        
        # parse contexts
        self.contexts = {}
        contextsElement = hlgElement.find('contexts')
        firstContext = True
        for contextElement in contextsElement.findall('context'):
            context = Context(self, contextElement)
            self.contexts[context.name] = context
            if firstContext:
                firstContext = False
                self.defaultContext = context
        
        # TODO parse itemData

    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = 'Syntax %s\n' % self.name
        for name, value in vars(self).iteritems():
            if not name.startswith('_') and \
               not name in ('defaultContext'):
                res += '\t%s: %s\n' % (name, value)
        
        res += '\tDefault context: %s\n' % self.defaultContext.name

        for listName, listValue in self.lists.iteritems():
            res += '\tList %s: %s\n' % (listName, listValue)
        
        
        for context in self.contexts.values():
            res += str(context)
        
        return res
