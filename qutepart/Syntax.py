"""Kate syntax definition parser and representation
Read http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/ 
if you want to understand something
"""

import os.path
import re
import xml.etree.ElementTree


class AbstractRule:
    """Base class for rule classes
    
    Public properties:
        formatName - Format name for matched text
        contextOperation - String, which represents context modification, which shall be applied, if rule matched
                  None, if not set
    """
    def __init__(self, parentContext, xmlElement):
        """Parse XML definition
        """
        self.parentContext = parentContext
        
        # default values
        self.column = None

        for key, value in xmlElement.items():
            setattr(self, key, value)
        
        if self.column is not None:
            self.column = int(self.column)
        
        # Convert attribute name to format name
        self.formatName = parentContext.syntax.formatNameMap[self.attribute]
        del self.attribute  # not needed
        
        # rename .context property
        if hasattr(self, 'context'):
            self.contextOperation = self.context
            del self.context

    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\t\tRule %s\n' % self.__class__.__name__
        for name, value in vars(self).iteritems():
            if not name == 'parentContext' and \
               not name.startswith('_') and \
               value is not None:
                res += '\t\t\t%s: %s\n' % (name, repr(value))
        return res
    
    def tryMatch(self, text):
        """Try to find themselves in the text.
        Returns matched length, or None if not matched
        """
        raise NotImplementedFault()
    
    def shortId(self):
        """Get short ID string of the rule. Used for logs
        i.e. "DetectChar(x)"
        """
        raise NotImplementedFault()


class DetectChar(AbstractRule):
    def tryMatch(self, text):
        if text[0] == self.char:
            return 1
        return None
    
    def shortId(self):
        return 'DetectChar(%s)' % self.char

class Detect2Chars(AbstractRule):
    def __init__(self, *args):
        AbstractRule.__init__(self, *args)
        self._string = self.char + self.char1
    
    def tryMatch(self, text):
        if text.startswith(self._string):
            return len(self._string)
        
        return None
    
    def shortId(self):
        return 'Detect2Chars(%s)' % self._string


class AnyChar(AbstractRule):
    pass

class StringDetect(AbstractRule):
    def tryMatch(self, text):
        if text.startswith(self.String):
            return len(self.String)
    
        return None
        
    def shortId(self):
        return 'StringDetect(%s)' % self.String

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

    def tryMatch(self, text):
        match = self._regExp.match(text)
        if match is not None:
            return len(match.group(0))
        
        return None
    
    def shortId(self):
        return 'RegExpr(%s)' % self.String


class keyword(AbstractRule):
    def tryMatch(self, text):
        if not self.parentContext.syntax.casesensitive:
            text = text.lower()
        
        for word in self.parentContext.syntax.lists[self.String]:
            if text.startswith(word):
                return len(word)
        
        return None

    def shortId(self):
        return 'keyword(%s)' % repr(self.String)


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
    """Highlighting context
    
    Public attributes:
        formatName - format name, which is used if no rules match
    """
    
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
        
        # Convert attribute name to format name
        self.formatName = syntax.formatNameMap[self.attribute]
        del self.attribute  # not needed
        
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
            if not name in ('rules', 'syntax', 'name'):
                res += '\t\t%s: %s\n' % (name, repr(value))
        
        for rule in self.rules:
            res += str(rule)
        return res


class Syntax:
    """Syntax file parser and container
    
    Public attributes:
        deliminatorSet - Set of deliminator characters
        casesensitive - Keywords are case sensetive. Global flag, every keyword might have own value

        formatNameMap - dictionary "attribute" : "format name"
        
        lists - Keyword lists as dictionary "list name" : "list value"
        
        defaultContext - Default context object
        contexts - Context list as dictionary "context name" : context
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
        
        # parse itemData
        self.formatNameMap = {}
        itemDatasElement = hlgElement.find('itemDatas')
        for item in itemDatasElement.findall('itemData'):
            self.formatNameMap[item.get('name')] = item.get('defStyleNum')
        
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
               not name in ('defaultContext', 'deliminatorSet', 'contexts'):
                res += '\t%s: %s\n' % (name, repr(value))
        
        res += '\tDefault context: %s\n' % self.defaultContext.name

        for listName, listValue in self.lists.iteritems():
            res += '\tList %s: %s\n' % (listName, listValue)
        
        
        for context in self.contexts.values():
            res += str(context)
        
        return res

    def parseBlock(self, text):
        """Parse block and return next structure:
            [ (Context, length, [matchedRules]), ...]
        where matchedRule is:
            (Rule, pos, length)
        """
        contextStack = [self.defaultContext]
        
        matchedContexts = []
        
        currentColumnIndex = 0
        while currentColumnIndex < len(text):
            length, newContextStack, matchedRules = \
                        self._parseBlockWithContextStack(contextStack, currentColumnIndex, text)
            
            matchedContexts.append((contextStack[-1], length, matchedRules))
            
            contextStack = newContextStack
            currentColumnIndex += length
        
        return matchedContexts

    def _parseBlockWithContextStack(self, contextStack, currentColumnIndex, text):
        """Parse block, using context
        Returns (length, newContextStack, matchedRules)
        where matchedRules is:
            (Rule, pos, length)
        """
        currentContext = contextStack[-1]
        
        startColumnIndex = currentColumnIndex
        matchedRules = []
        while currentColumnIndex < len(text):
            
            for rule in currentContext.rules:
                # Skip if column doesn't match
                if rule.column is not None and \
                   rule.column != currentColumnIndex:
                    continue
                
                # Try to find rule match
                count = rule.tryMatch(text[currentColumnIndex:])
                if count is not None:
                    matchedRules.append((rule, currentColumnIndex, count))
                    currentColumnIndex += count
                    
                    if rule.contextOperation is not None:
                        newContextStack = self._generateNextContextStack(contextStack, rule.contextOperation)
                        return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)
                    
                    break

            currentColumnIndex += 1
        
        return (currentColumnIndex - startColumnIndex, contextStack, matchedRules)

    def parseBlockTextualResults(self, text):
        """Execute parseBlock() and return textual results.
        For debugging"""
        parseBlockResult = self.parseBlock(text)
        return [ (context.name, contextLength, [ (rule.shortId(), pos, length) \
                                                    for rule, pos, length in matchedRules]) \
                    for context, contextLength, matchedRules in parseBlockResult]

    def _generateNextContextStack(self, currentStack, operation):
        """Apply context modification to the context stack.
        Returns new object, if stack has been modified
        """
        # FIXME context name and pops count validation
        
        if not operation:
            return currentStack

        if operation == '#stay':
            return currentStack
        elif operation.startswith('#pop'):
            return self._generateNextContextStack(currentStack[1:], operation[len ('#pop'):])
        else:  # context name
            return currentStack + [self.contexts[operation]]  # no .append, shall not modify current stack
        # FIXME doPopsAndPush not supported. I can't understand kate code
