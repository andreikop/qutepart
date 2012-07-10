"""Kate syntax definition parser and representation
Read http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/ 
if you want to understand something
"""

import os.path
import xml.etree.ElementTree

class AbstractRule:
    """Base class for rule classes
    """
    def __init__(self, xmlElement):
        for key, value in xmlElement.items():
            setattr(self, key, value)
    
    def __str__(self):
        res = '\t\tRule %s\n' % self.__class__.__name__
        for name, value in vars(self).iteritems():
            res += '\t\t\t%s: %s\n' % (name, value)
        return res


class DetectChar(AbstractRule):
    pass
class Detect2Chars(AbstractRule):
    pass
class AnyChar(AbstractRule):
    pass
class StringDetect(AbstractRule):
    pass
class WordDetect(AbstractRule):
    pass
class RegExpr(AbstractRule):
    pass
class keyword(AbstractRule):
    pass
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
    def __init__(self, xmlElement):
        """Construct context from XML element
        """
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
            rule = ruleClassDict[ruleElement.tag](ruleElement)
            self.rules.append(rule)
    
    def __str__(self):
        res = '\tContext %s\n' % self.name
        for name, value in vars(self).iteritems():
            if name != 'rules':
                res += '\t\t%s: %s\n' % (name, value)
        
        for rule in self.rules:
            res += str(rule)
        return res


class Syntax:
    """Syntax file parser and container
    """
    def __init__(self, fileName):
        modulePath = os.path.dirname(__file__)
        dataFilePath = os.path.join(modulePath, "syntax", fileName)
        with open(dataFilePath, 'r') as dataFile:
            root = xml.etree.ElementTree.parse(dataFile).getroot()
        
        # read attributes
        for key, value in root.items():
            setattr(self, key, value)
        
        hlgElement = root.find('highlighting')
        
        # parse lists
        self._lists = {}  # list name: list
        for listElement in hlgElement.findall('list'):
            items = [item.text \
                        for item in listElement.findall('item')]
            self._lists[listElement.attrib['name']] = items

        # parse contexts
        self._contexts = {}
        contextsElement = hlgElement.find('contexts')
        firstContext = True
        for contextElement in contextsElement.findall('context'):
            context = Context(contextElement)
            self._contexts[context.name] = context
            if firstContext:
                firstContext = False
                self.defaultContext = context
        
        # TODO parse itemData

    def __str__(self):
        res = 'Syntax %s\n' % self.name
        for name, value in vars(self).iteritems():
            if not name.startswith('_') and \
               not name in ('defaultContext'):
                res += '\t%s: %s\n' % (name, value)
        
        res += '\tDefault context: %s\n' % self.defaultContext.name

        for listName, listValue in self._lists.iteritems():
            res += '\tList %s: %s\n' % (listName, listValue)
        
        
        for context in self._contexts.values():
            res += str(context)
        
        return res
