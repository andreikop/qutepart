"""Kate syntax definition parser and representation
Read http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/ 
if you want to understand something


"attribute" property of rules and contexts contains not an original string, 
but value from itemDatas section (style name)
"""

import os.path
import sys
import re
import copy
import xml.etree.ElementTree

def _parseBoolAttribute(value):
    if value in ('true', '1'):
        return True
    elif value in ('false', '0'):
        return False
    else:
        raise UserWarning("Invalid bool attribute value '%s'" % value)

def _safeGetRequiredAttribute(xmlElement, name, default):
    if name in xmlElement.attrib:
        return xmlElement.attrib[name]
    else:
        print >> sys.stderr, "Required attribute '%s' is not set for element '%s'" % (name, xmlElement.tag)
        return default

class AbstractRule:
    """Base class for rule classes
    """
    def __init__(self, parentContext, xmlElement):
        """Parse XML definition
        """
        self.parentContext = parentContext
        
        # attribute
        attribute = xmlElement.attrib.get("attribute", None)
        if attribute is not None:
            self.attribute = parentContext.syntax._mapAttributeToStyle(attribute)
        else:
            self.attribute = None

        # context
        context = xmlElement.attrib.get("context", None)
        if context is not None:
            self.context = context
        else:
            self.context = None
    
        # TODO beginRegion
        # TODO endRegion
        # TODO lookAhead
        # TODO firstNonSpace
        
        column = xmlElement.attrib.get("column", None)
        if column is not None:
            self.column = int(column)
        else:
            self.column = None
        
    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\t\tRule %s\n' % self.shortId()
        res += '\t\t\tstyleName: %s\n' % self.attribute
        res += '\t\t\tcontext: %s\n' % self.context
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
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._char = _safeGetRequiredAttribute(xmlElement, "char", None)
    
    def tryMatch(self, text):
        if self._char is None:
            return None
        
        if text[0] == self._char:
            return 1
        return None
    
    def shortId(self):
        return 'DetectChar(%s)' % self._char

class Detect2Chars(AbstractRule):    
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        
        char = _safeGetRequiredAttribute(xmlElement, 'char', None)
        char1 = _safeGetRequiredAttribute(xmlElement, 'char1', None)
        if char is None or char1 is None:
            self._string = None
        else:
            self._string = char + char1
    
    def tryMatch(self, text):
        if self._string is None:
            return None
        
        if text.startswith(self._string):
            return len(self._string)
        
        return None
    
    def shortId(self):
        return 'Detect2Chars(%s)' % self._string


class AnyChar(AbstractRule):
    pass

class StringDetect(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', None)

    def tryMatch(self, text):
        if self._string is None:
            return
        
        if text.startswith(self._string):
            return len(self._string)
    
        return None
        
    def shortId(self):
        return 'StringDetect(%s)' % self._string

class WordDetect(AbstractRule):
    pass


class RegExpr(AbstractRule):
    """TODO if regexp starts with ^ - match only column 0
    TODO support "minimal" flag
    """
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        
        string = _safeGetRequiredAttribute(xmlElement, 'String', None)        
        if string is None:
            self._regExp = None
            return
        string = self._processCraracterCodes(string)
        
        insensitive = xmlElement.attrib.get('insensitive', False)
        flags = 0
        if insensitive:
            flags = re.IGNORECASE
        
        try:
            self._regExp = re.compile(string)
        except (re.error, AssertionError) as ex:
            print >> sys.stderr, "Invalid pattern '%s': %s" % (string, str(ex))
            self._regExp = None

    def _processCraracterCodes(self, text):
        """QRegExp use \0ddd notation for character codes, where d in octal digit
        i.e. \0377 is character with code 255 in the unicode table
        Convert such notation to unicode text
        """
        text = unicode(text)
        def replFunc(matchObj):
            matchText = matchObj.group(0)
            charCode = eval(matchText[1:])
            return chr(charCode).decode('latin1')
        return re.sub(r"\\0\d\d\d", replFunc, text)
        
    def tryMatch(self, text):
        if self._regExp is None:
            return None

        match = self._regExp.match(text)
        if match is not None and match.group(0):
            return len(match.group(0))
        
        return None
    
    def shortId(self):
        return 'RegExpr(%s)' % self._regExp.pattern


class keyword(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', None)

    def tryMatch(self, text):
        if self._string is None:
            return None

        if not self.parentContext.syntax.casesensitive:
            text = text.lower()
        
        for word in self.parentContext.syntax.lists[self._string]:
            if text.startswith(word):
                return len(word)
        
        return None

    def shortId(self):
        return 'keyword(%s)' % repr(self._string)


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
    """
    
    def __init__(self, syntax, xmlElement):
        """Construct context from XML element
        """
        self.syntax = syntax

        self.name = _safeGetRequiredAttribute(xmlElement, 'name', 'Error: context name is not set!!!')
        
        attribute = _safeGetRequiredAttribute(xmlElement, 'attribute', 'normal')
        self.attribute = syntax._mapAttributeToStyle(attribute)
        
        self.lineEndContext = xmlElement.attrib.get('lineEndContext', '#stay')
        self.lineBeginContext = xmlElement.attrib.get('lineEndContext', '#stay')
        
        if _parseBoolAttribute(xmlElement.attrib.get('fallthrough', 'false')):
            self.fallthroughContext = _safeGetRequiredAttribute(xmlElement, 'fallthroughContext', None)
        else:
            self.fallthroughContext = None
        
        self.dynamic = xmlElement.attrib.get('dynamic', False)
        
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
        res += '\t\t%s: %s\n' % ('attribute', self.attribute)
        res += '\t\t%s: %s\n' % ('lineEndContext', self.lineEndContext)
        res += '\t\t%s: %s\n' % ('lineBeginContext', self.lineBeginContext)
        if self.fallthroughContext is not None:
            res += '\t\t%s: %s\n' % ('fallthroughContext', self.fallthroughContext)
        res += '\t\t%s: %s\n' % ('dynamic', self.dynamic)
        
        for rule in self.rules:
            res += str(rule)
        return res


class Syntax:
    """Syntax file parser and container
    
    Public attributes:
        deliminatorSet - Set of deliminator characters
        casesensitive - Keywords are case sensetive. Global flag, every keyword might have own value

        lists - Keyword lists as dictionary "list name" : "list value"
        
        defaultContext - Default context object
        contexts - Context list as dictionary "context name" : context
    """
    
    _DEFAULT_DELIMINATOR = " \t.():!+,-<=>%&*/;?[]^{|}~\\"

    _DEFAULT_ATTRIBUTE_TO_STYLE_MAP = \
    {
        'alert' : 'dsAlert',
        'base-n integer' : 'dsBaseN',
        'character' : 'dsChar',
        'string char': 'dsChar',
        'comment' : 'dsComment',
        'data type' : 'dsDataType',
        'decimal/value' : 'dsDecVal',
        'error' : 'dsError',
        'floating point' : 'dsFloat',
        'function' : 'dsFunction',
        'keyword' : 'dsKeyword',
        'normal' : 'dsNormal',
        'others' : 'dsOthers',
        'region marker' : 'dsRegionMarker',
        'string' : 'dsString'
    }
    
    _KNOWN_STYLES = set([  "dsNormal",
                           "dsKeyword",
                           "dsDataType",
                           "dsDecVal",
                           "dsBaseN",
                           "dsFloat",
                           "dsChar",
                           "dsString",
                           "dsComment",
                           "dsOthers",
                           "dsAlert",
                           "dsFunction",
                           "dsRegionMarker",
                           "dsError",
                           "CustomTmpForDebugging"])

    def __init__(self, fileName):
        """Parse XML definition
        """
        
        modulePath = os.path.dirname(__file__)
        dataFilePath = os.path.join(modulePath, "syntax", fileName)
        with open(dataFilePath, 'r') as dataFile:
            root = xml.etree.ElementTree.parse(dataFile).getroot()

        self.name = _safeGetRequiredAttribute(root, 'name', 'Error: Syntax name is not set!!!')
        
        self.section = _safeGetRequiredAttribute(root, 'section', 'Error: Section is not set!!!')
        self.extensions = _safeGetRequiredAttribute(root, 'extensions', '')
        
        self.mimetype = root.attrib.get('mimetype', None)
        self.version = root.attrib.get('version', None)
        self.kateversion = root.attrib.get('kateversion', None)
        
        self.casesensitive = _parseBoolAttribute(root.attrib.get('casesensitive', 'true'))
        
        self.priority = root.attrib.get('priority', None)
        self.author = root.attrib.get('author', None)
        self.license = root.attrib.get('license', None)
        
        self.hidden = _parseBoolAttribute(root.attrib.get('hidden', 'false'))
        
        self.deliminatorSet = set(Syntax._DEFAULT_DELIMINATOR)
        
        hlgElement = root.find('highlighting')
        
        # parse lists
        self.lists = {}  # list name: list
        for listElement in hlgElement.findall('list'):
            items = [item.text \
                        for item in listElement.findall('item')]
            name = _safeGetRequiredAttribute(listElement, 'name', 'Error: list name is not set!!!')
            self.lists[name] = items
        
        # Make all keywords lowercase, if syntax is not case sensetive
        if not self.casesensitive:
            for keywordList in self.lists.values():
                for index, keyword in enumerate(keywordList):
                    keywordList[index] = keyword.lower()
        
        # parse itemData
        self._styleNameMap = copy.copy(self._DEFAULT_ATTRIBUTE_TO_STYLE_MAP)
        itemDatasElement = hlgElement.find('itemDatas')
        for item in itemDatasElement.findall('itemData'):
            name, styleName = item.get('name'), item.get('defStyleNum')
            
            if styleName is None:  # custom format
                styleName = 'CustomTmpForDebugging'
            
            if not styleName in self._KNOWN_STYLES:
                print >> sys.stderr, "Unknown default style '%s'" % styleName
                styleName = 'dsNormal'
            name = name.lower()  # format names are not case sensetive
            self._styleNameMap[name] = styleName
        
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
               not name in ('defaultContext', 'deliminatorSet', 'contexts', 'lists') and \
               not value is None:
                res += '\t%s: %s\n' % (name, value)
        
        res += '\tDefault context: %s\n' % self.defaultContext.name

        for listName, listValue in self.lists.iteritems():
            res += '\tList %s: %s\n' % (listName, listValue)
        
        
        for context in self.contexts.values():
            res += str(context)
        
        return res
    
    def _mapAttributeToStyle(self, attribute):
        """Maps 'attribute' field of a Context and a Rule to style
        """
        if not attribute.lower() in self._styleNameMap:
            print >> sys.stderr, "Unknown attribute '%s'" % attribute
            return self._styleNameMap['normal']
        
        # attribute names are not case sensetive
        return self._styleNameMap[attribute.lower()]

    def parseBlock(self, text, prevLineData):
        """Parse block and return touple:
            (lineData, matchedRules)
        where matchedContexts is:
            [ (Context, length, [matchedRules]), ...]
        where matchedRule is:
            (Rule, pos, length)
        """
        if prevLineData is not None:
            contextStack = prevLineData
        else:
            contextStack = [self.defaultContext]
        
        matchedContexts = []
        
        currentColumnIndex = 0
        while currentColumnIndex < len(text):
            length, newContextStack, matchedRules = \
                        self._parseBlockWithContextStack(contextStack, currentColumnIndex, text)
            
            matchedContexts.append((contextStack[-1], length, matchedRules))
            
            contextStack = newContextStack
            currentColumnIndex += length
        
        return contextStack, matchedContexts

    def _parseBlockWithContextStack(self, contextStack, currentColumnIndex, text):
        """Parse block, using last context in the stack.
        Exits, when reached end of the text, or when context is switched
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
                    continue  # for loop iteration
                
                # Try to find rule match
                count = rule.tryMatch(text[currentColumnIndex:])
                if count is not None:
                    matchedRules.append((rule, currentColumnIndex, count))
                    currentColumnIndex += count
                    
                    if rule.context is not None:
                        newContextStack = self._generateNextContextStack(contextStack, rule.context)
                        if newContextStack != contextStack:
                            return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)
                    
                    break  # for loop

            currentColumnIndex += 1

        if contextStack[-1].lineEndContext is not None:
            contextStack = self._generateNextContextStack(contextStack, contextStack[-1].lineEndContext)
        
        return (currentColumnIndex - startColumnIndex, contextStack, matchedRules)

    def parseBlockTextualResults(self, text, prevLineData=None):
        """Execute parseBlock() and return textual results.
        For debugging"""
        lineData, matchedContexts = self.parseBlock(text, prevLineData)
        lineDataTextual = [context.name for context in lineData]
        matchedContextsTextual = \
         [ (context.name, contextLength, [ (rule.shortId(), pos, length) \
                                                    for rule, pos, length in matchedRules]) \
                    for context, contextLength, matchedRules in matchedContexts]
        
        return matchedContextsTextual

    def parseBlockContextStackTextual(self, text, prevLineData=None):
        """Execute parseBlock() and return context stack as list of context names
        For debugging"""
        lineData, matchedContexts = self.parseBlock(text, prevLineData)
        lineDataTextual = [context.name for context in lineData]
        
        return lineDataTextual

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
            return self._generateNextContextStack(currentStack[:-1], operation[len ('#pop'):])
        else:  # context name
            return currentStack + [self.contexts[operation]]  # no .append, shall not modify current stack
        # FIXME doPopsAndPush not supported. I can't understand kate code
