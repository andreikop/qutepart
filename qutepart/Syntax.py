"""Kate syntax definition parser and representation
Read http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/ 
if you want to understand something


'attribute' property of rules and contexts contains not an original string, 
but value from itemDatas section (style name)

'context', 'lineBeginContext', 'lineEndContext', 'fallthroughContext' properties
contain not a text value, but _ContextSwitcher object
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


class _ContextSwitcher:
    """Class parses 'context', 'lineBeginContext', 'lineEndContext', 'fallthroughContext'
    and modifies context stack according to context operation
    """
    def __init__(self, contextOperation, contexts):
        self._contextOperation = contextOperation
        
        self._popsCount = 0
        self._contextToSwitch = None
        
        rest = contextOperation
        while rest.startswith('#pop'):
            self._popsCount += 1
            rest = rest[len('#pop'):]
        
        if rest == '#stay':
            if self._popsCount:
                print >> sys.stderr, "Invalid context operation '%s'" % contextOperation
        elif rest in contexts:
            self._contextToSwitch = contexts[rest]
        elif rest.startswith('##'):
            pass  # TODO implement IncludeRules
        elif rest:
            print >> sys.stderr, "Unknown context '%s'" % rest
    
    def __str__(self):
        return self._contextOperation
        
    def getNextContextStack(self, contextStack):
        """Apply modification to the contextStack.
        This method never modifies input parameter list
        """
        if self._popsCount:
            if len(contextStack) < self._popsCount or \
               len(contextStack) == self._popsCount and self._contextToSwitch is None:
                print >> sys.stderr, "Error: #pop value is too big"
            
            contextStack = contextStack[:-self._popsCount]
        
        if self._contextToSwitch is not None:
            return contextStack + [self._contextToSwitch]
        else:
            return contextStack
        
    
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
        contextText = xmlElement.attrib.get("context", '#stay')
        self.context = _ContextSwitcher(contextText, parentContext.syntax.contexts)
    
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
    
    def tryMatch(self, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (count, matchedRule) or (None, None) if doesn't match
        
        IncludeRules reimplements this method
        """
        # Skip if column doesn't match
        if self.column is not None and \
           self.column != currentColumnIndex:
            return None, None
        
        count = self._tryMatch(text)
        if count is not None:
            return count, self
        else:
            return None, None

    def _tryMatch(self, text):
        """Simple tryMatch method. Checks if text matches.
        Shall be reimplemented by child classes
        """
        raise NotImplementedFault()
    
    def shortId(self):
        """Get short ID string of the rule. Used for logs
        i.e. "DetectChar(x)"
        """
        raise NotImplementedError(str(self.__class__))


class DetectChar(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._char = _safeGetRequiredAttribute(xmlElement, "char", None)
    
    def _tryMatch(self, text):
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
    
    def _tryMatch(self, text):
        if self._string is None:
            return None
        
        if text.startswith(self._string):
            return len(self._string)
        
        return None
    
    def shortId(self):
        return 'Detect2Chars(%s)' % self._string


class AnyChar(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', '')
    
    def _tryMatch(self, text):
        if text[0] in self._string:
            return 1
        
        return None

    def shortId(self):
        return 'AnyChar(%s)' % self._string


class StringDetect(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', None)

    def _tryMatch(self, text):
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
        
    def _tryMatch(self, text):
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

    def _tryMatch(self, text):
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
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._contextName = _safeGetRequiredAttribute(xmlElement, "context", None)
        if self._contextName is not None:
            if self._contextName in self.parentContext.syntax.contexts:
                self.context = self.parentContext.syntax.contexts[self._contextName]
            else:
                print >> sys.stderr, "Reference to unknown context", self._contextName
                self.context = self.parentContext.syntax.defaultContext
        else:
            self.context = self.parentContext.syntax.defaultContext

    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\t\tRule %s\n' % self.shortId()
        res += '\t\t\tstyleName: %s\n' % self.attribute
        return res

    def shortId(self):
        return "IncludeRules(%s)" % self._contextName
    
    def tryMatch(self, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (count, matchedRule) or (None, None) if doesn't match
        """
        for rule in self.context.rules:
            columnIndex, text = rule.tryMatch(currentColumnIndex, text)
            if columnIndex is not None:
                return (columnIndex, text)
        else:
            return None, None


class DetectSpaces(AbstractRule):
    def shortId(self):
        return 'DetectSpaces()'

    def _tryMatch(self, text):
        spaceLen = len(text) - len(text.lstrip())
        if spaceLen:
            return spaceLen
        else:
            return None
        
class DetectIdentifier(AbstractRule):
    pass

_ruleClasses = (DetectChar, Detect2Chars, AnyChar, StringDetect, WordDetect, RegExpr,
                keyword, Int, Float, HlCOct, HlCHex, HlCStringChar, HlCChar, RangeDetect,
                LineContinue, IncludeRules, DetectSpaces, DetectIdentifier)


class Context:
    """Highlighting context
    """
    def __init__(self, syntax, xmlElement):
        self.syntax = syntax
        self.name = _safeGetRequiredAttribute(xmlElement, 'name', 'Error: context name is not set!!!')
        self._xmlElement = xmlElement

    def load(self):
        """Construct context from XML element
        Contexts are at first constructed, and only then loaded, because when loading context,
        _ContextSwitcher must have references to all defined contexts
        """
        attribute = _safeGetRequiredAttribute(self._xmlElement, 'attribute', 'normal')
        self.attribute = self.syntax._mapAttributeToStyle(attribute)
        
        lineEndContextText = self._xmlElement.attrib.get('lineEndContext', '#stay')
        self.lineEndContext = _ContextSwitcher(lineEndContextText,  self.syntax.contexts)
        lineBeginContextText = self._xmlElement.attrib.get('lineEndContext', '#stay')
        self.lineBeginContext = _ContextSwitcher(lineBeginContextText, self.syntax.contexts)
        
        if _parseBoolAttribute(self._xmlElement.attrib.get('fallthrough', 'false')):
            fallthroughContextText = _safeGetRequiredAttribute(self._xmlElement, 'fallthroughContext', '#stay')
            self.fallthroughContext = _ContextSwitcher(fallthroughContextText, self.syntax.contexts)
        else:
            self.fallthroughContext = None
        
        self.dynamic = self._xmlElement.attrib.get('dynamic', False)
        
        # load rules
        self.rules = []

        ruleClassDict = {}
        for ruleClass in _ruleClasses:
            ruleClassDict[ruleClass.__name__] = ruleClass
        
        for ruleElement in self._xmlElement.getchildren():
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
        self.extensions = _safeGetRequiredAttribute(root, 'extensions', '').split(';')
        
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
        
        # parse contexts stage 1: create objects
        self.contexts = {}
        contextsElement = hlgElement.find('contexts')
        firstContext = True
        
        for contextElement in contextsElement.findall('context'):
            context = Context(self, contextElement)
            self.contexts[context.name] = context
            if firstContext:
                firstContext = False
                self.defaultContext = context
        
        # parse contexts stage 2: load contexts
        for context in self.contexts.values():
            context.load()

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
        
        # this code is not tested, because lineBeginContext is not defined by any xml file
        if contextStack[-1].lineBeginContext is not None:
            contextStack = contextStack[-1].lineBeginContext.getNextContextStack(contextStack)
        
        matchedContexts = []
        
        currentColumnIndex = 0
        while currentColumnIndex < len(text):
            length, newContextStack, matchedRules = \
                        self._parseBlockWithContextStack(contextStack, currentColumnIndex, text)
            
            matchedContexts.append((contextStack[-1], length, matchedRules))
            
            contextStack = newContextStack
            currentColumnIndex += length

        if contextStack[-1].lineEndContext is not None:
            contextStack = contextStack[-1].lineEndContext.getNextContextStack(contextStack)
        
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
                count, matchedRule = rule.tryMatch(currentColumnIndex, text[currentColumnIndex:])
                if count is not None:
                    matchedRules.append((matchedRule, currentColumnIndex, count))
                    currentColumnIndex += count
                    
                    if matchedRule.context is not None:
                        newContextStack = matchedRule.context.getNextContextStack(contextStack)
                        if newContextStack != contextStack:
                            return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)
                    
                    break  # for loop                    
            else:
                if currentContext.fallthroughContext is not None:
                    newContextStack = currentContext.fallthroughContext.getNextContextStack(contextStack)
                    if newContextStack != contextStack:
                        return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)

            currentColumnIndex += 1

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
