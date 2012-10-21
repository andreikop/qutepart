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
    if value.lower() in ('true', '1'):
        return True
    elif value.lower() in ('false', '0'):
        return False
    else:
        raise UserWarning("Invalid bool attribute value '%s'" % value)

def _safeGetRequiredAttribute(xmlElement, name, default):
    if name in xmlElement.attrib:
        return xmlElement.attrib[name]
    else:
        print >> sys.stderr, "Required attribute '%s' is not set for element '%s'" % (name, xmlElement.tag)
        return default

class _ContextStack:
    def __init__(self, contexts, data):
        """Create default context stack for syntax
        Contains default context on the top
        """
        self._contexts = contexts
        self._data = data
    
    @staticmethod
    def makeDefault(syntax):
        """Make default stack for syntax
        """
        return _ContextStack([syntax.defaultContext], [None])

    def pop(self, count):
        """Returns new context stack, which doesn't contain few levels
        """
        if len(self._contexts) < count:
            print >> sys.stderr, "Error: #pop value is too big"
            count = 0
        return _ContextStack(self._contexts[:-count], self._data[:-count])
    
    def append(self, context, data):
        """Returns new context, which contains current stack and new frame
        """
        return _ContextStack(self._contexts + [context], self._data + [data])
    
    def currentContext(self):
        """Get current context
        """
        return self._contexts[-1]
    
    def currentData(self):
        """Get current data
        """
        return self._data[-1]
        

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
        
    def getNextContextStack(self, contextStack, data=None):
        """Apply modification to the contextStack.
        This method never modifies input parameter list
        """
        if self._popsCount:
            contextStack = contextStack.pop(self._popsCount)
        
        if self._contextToSwitch is not None:
            if not self._contextToSwitch.dynamic:
                data = None
            contextStack = contextStack.append(self._contextToSwitch, data)
        
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
    
        self.lookAhead = _parseBoolAttribute(xmlElement.attrib.get("lookAhead", "false"))
        self.firstNonSpace = _parseBoolAttribute(xmlElement.attrib.get("firstNonSpace", "false"))
        self.dynamic = _parseBoolAttribute(xmlElement.attrib.get("dynamic", "false"))
        
        # TODO beginRegion
        # TODO endRegion
        
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
    
    def shortId(self):
        """Get short ID string of the rule. Used for logs
        i.e. "DetectChar(x)"
        """
        raise NotImplementedError(str(self.__class__))

    def tryMatch(self, contextStack, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (contextStack, count, matchedRule) or (contextStack, None, None) if doesn't match
        """
        # Skip if column doesn't match
        if self.column is not None and \
           self.column != currentColumnIndex:
            return contextStack,None, None
        
        if self.firstNonSpace:
            if currentColumnIndex != 0 and \
               text[currentColumnIndex - 1].isspace():
                return contextStack,None, None
        
        newContextStack, count, matchedRule = self._tryMatch(contextStack, currentColumnIndex, text)
        if count is None:  # no match
            return newContextStack, None, None
        
        if self.lookAhead:
            count = 0
        
        return newContextStack, count, matchedRule

    def _tryMatch(self, contextStack, currentColumnIndex, text):
        """Internal method.
        Doesn't check current column and lookAhead
        
        This is basic implementation. IncludeRules, WordDetect, Int, Float reimplements this method
        """
        count = self._tryMatchText(text[currentColumnIndex:], contextStack.currentData())
        if count is not None:
            if self.context is not None:
                contextStack = self.context.getNextContextStack(contextStack)
            return contextStack, count, self
        else:
            return contextStack, None, None
    
    _seqReplacer = re.compile('%\d+')
    
    def _tryMatchText(self, text, contextData):
        """Simple tryMatch method. Checks if text matches.
        Shall be reimplemented by child classes
        """
        raise NotImplementedFault()
    

class DetectChar(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._char = _safeGetRequiredAttribute(xmlElement, "char", None)
    
    def shortId(self):
        return 'DetectChar(%s)' % self._char
    
    def _tryMatchText(self, text, contextData):
        if self._char is None:
            return None
        
        if text[0] == self._char:
            return 1
        return None

class Detect2Chars(AbstractRule):    
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        
        char = _safeGetRequiredAttribute(xmlElement, 'char', None)
        char1 = _safeGetRequiredAttribute(xmlElement, 'char1', None)
        if char is None or char1 is None:
            self._string = None
        else:
            self._string = char + char1
    
    def shortId(self):
        return 'Detect2Chars(%s)' % self._string
    
    def _tryMatchText(self, text, contextData):
        if self._string is None:
            return None
        
        if text.startswith(self._string):
            return len(self._string)
        
        return None


class AnyChar(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', '')

    def shortId(self):
        return 'AnyChar(%s)' % self._string
    
    def _tryMatchText(self, text, contextData):
        if text[0] in self._string:
            return 1
        
        return None


class StringDetect(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', None)
        
    def shortId(self):
        return 'StringDetect(%s)' % self._string

    def _tryMatchText(self, text, contextData):
        if self._string is None:
            return
        
        if self.dynamic:
            string = self._makeDynamicStringSubsctitutions(self._string)
        else:
            string = self._string
        
        if text.startswith(string):
            return len(string)
    
        return None
    
    @staticmethod
    def _makeDynamicStringSubsctitutions(string, contextData):
        """For dynamic rules, replace %d patterns with actual strings
        """
        def _replaceFunc(escapeMatchObject):
            stringIndex = escapeMatchObject.group(0)[1]
            index = int(stringIndex) - 1
            if index < len(contextData):
                return contextData[index]
            else:
                return escapeMatchObject.group(0)  # no any replacements, return original value

        return AbstractRule._seqReplacer.sub(_replaceFunc, string)


class AbstractWordRule(AbstractRule):
    """Base class for WordDetect and keyword
    """
    def _tryMatch(self, contextStack, currentColumnIndex, text):
        # Skip if column doesn't match        
        wordStart = currentColumnIndex == 0 or \
                    text[currentColumnIndex - 1].isspace() or \
                    text[currentColumnIndex - 1] in self.parentContext.syntax.deliminatorSet
        
        if not wordStart:
            return contextStack, None, None
        
        textToCheck = text[currentColumnIndex:]
        
        for word in self._words:
            if not textToCheck.startswith(word):
                continue
                
            stringLen = len(word)
            wordEnd   = stringLen == len(textToCheck) or \
                        textToCheck[stringLen].isspace() or \
                        textToCheck[stringLen] in self.parentContext.syntax.deliminatorSet
            
            if not wordEnd:
                continue

            if self.context is not None:
                contextStack = self.context.getNextContextStack(contextStack)

            return contextStack, stringLen, self
        else:
            return contextStack, None, None

class WordDetect(AbstractWordRule):
    def __init__(self, parentContext, xmlElement):
        AbstractWordRule.__init__(self, parentContext, xmlElement)
        
        self._words = [_safeGetRequiredAttribute(xmlElement, "String", "")]
        
        self._insensitive = _parseBoolAttribute(xmlElement.attrib.get("insensitive", "false"))
    
    def shortId(self):
        return 'WordDetect(%s, %s)' % (self._string, self._insensitive)


class keyword(AbstractWordRule):
    def __init__(self, parentContext, xmlElement):
        AbstractWordRule.__init__(self, parentContext, xmlElement)
        
        self._string = _safeGetRequiredAttribute(xmlElement, 'String', None)
        try:
            self._words = self.parentContext.syntax.lists[self._string]
        except KeyError:
            print >> sys.stderr, 'List', self._string, 'not found'
            self._words = []

    def shortId(self):
        return 'keyword(%s)' % repr(self._string)


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
            
        self._string = self._processCraracterCodes(string)
        self._insensitive = xmlElement.attrib.get('insensitive', False)
        
        if not self.dynamic:
            self._regExp = self._compileRegExp(self._string, self._insensitive)
    
    @staticmethod
    def _compileRegExp(string, insensitive):
        flags = 0
        if insensitive:
            flags = re.IGNORECASE
        
        try:
            return re.compile(string)
        except (re.error, AssertionError) as ex:
            print >> sys.stderr, "Invalid pattern '%s': %s" % (string, str(ex))
            return None

    def shortId(self):
        return 'RegExpr(%s)' % self._string

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

    @staticmethod
    def _makeDynamicStringSubsctitutions(string, contextData):
        """For dynamic rules, replace %d patterns with actual strings
        AbstractRule method reimplementation. Escapes reg exp symbols in the pattern
        """
        def _replaceFunc(escapeMatchObject):
            stringIndex = escapeMatchObject.group(0)[1]
            index = int(stringIndex) - 1
            if index < len(contextData):
                return re.escape(contextData[index])
            else:
                return escapeMatchObject.group(0)  # no any replacements, return original value

        return AbstractRule._seqReplacer.sub(_replaceFunc, string)

    def _tryMatch(self, contextStack, currentColumnIndex, text):
        """Tries to parse text. If matched - saves data for dynamic context
        """
        if self.dynamic:
            string = self._makeDynamicStringSubsctitutions(self._string, contextStack.currentData())
            regExp = self._compileRegExp(string, self._insensitive)
        else:
            regExp = self._regExp
        
        if regExp is None:
            return None
        
        match = regExp.match(text[currentColumnIndex:])
        if match is not None and match.group(0):
            print self._string, regExp.pattern, match.groups()
            count = len(match.group(0))

            if self.context is not None:
                contextStack = self.context.getNextContextStack(contextStack, match.groups())
            return contextStack, count, self
        else:
            return contextStack, None, None


class AbstractNumberRule(AbstractRule):
    """Base class for Int and Float rules.
    This rules can have child rules
    """
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._childRules = _getChildRules(parentContext, xmlElement)

    def _tryMatch(self, contextStack, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (count, matchedRule) or (None, None) if doesn't match
        """        
        index = self._tryMatchText(text[currentColumnIndex:], contextStack.currentData())
        if index is None:
            return contextStack, None, None
        
        if currentColumnIndex + index < len(text):
            for rule in self._childRules:
                newContextStack, matchedLength, matchedRule = rule.tryMatch(contextStack, currentColumnIndex + index, text)
                if matchedLength is not None:
                    index += matchedLength
                    break
                # child rule context and attribute ignored
        
        if self.context is not None:
            contextStack = self.context.getNextContextStack(contextStack)

        return contextStack, index, self
    
    def _countDigits(self, text):
        """Count digits at start of text
        """
        index = 0
        while index < len(text):
            if not text[index].isdigit():
                break
            index += 1
        return index
    
class Int(AbstractNumberRule):
    def shortId(self):
        return 'Int()'

    def _tryMatchText(self, text, contextData):
        matchedLength = self._countDigits(text)
        
        if matchedLength:
            return matchedLength
        else:
            return None
    

class Float(AbstractNumberRule):
    def shortId(self):
        return 'Float()'

    def _tryMatchText(self, text, contextData):
        
        haveDigit = False
        havePoint = False
        
        matchedLength = 0
        
        digitCount = self._countDigits(text[matchedLength:])
        if digitCount:
            haveDigit = True
            matchedLength += digitCount
        
        if len(text) > matchedLength and text[matchedLength] == '.':
            havePoint = True
            matchedLength += 1
        
        digitCount = self._countDigits(text[matchedLength:])
        if digitCount:
            haveDigit = True
            matchedLength += digitCount
        
        if len(text) > matchedLength and text[matchedLength] == 'E':
            matchedLength += 1
            
            if len(text) > matchedLength and text[matchedLength] in '+-':
                matchedLength += 1
            
            haveDigitInExponent = False
            
            digitCount = self._countDigits(text[matchedLength:])
            if digitCount:
                haveDigitInExponent = True
                matchedLength += digitCount
            
            if not haveDigitInExponent:
                return None
            
            return matchedLength
        else:
            if not havePoint:
                return None
        
        if matchedLength and haveDigit:
            return matchedLength
        else:
            return None
    

class HlCOct(AbstractRule):
    def shortId(self):
        return 'HlCOct'

    def _tryMatchText(self, text, contextData):
        if text[0] != '0':
            return None
        
        index = 1
        while index < len(text) and text[index] in '1234567':
            index += 1
        
        if index == 1:
            return None
        
        if index < len(text) and text[index].upper() in 'LU':
            index += 1
        
        return index

    def shortId(self):
        return 'HlCOct()'

class HlCHex(AbstractRule):
    def shortId(self):
        return 'HlCHex'

    def _tryMatchText(self, text, contextData):
        if len(text) < 3:
            return None
        
        if text[:2].upper() != '0X':
            return None
        
        index = 2
        while index < len(text) and text[index].upper() in '0123456789ABCDEF':
            index += 1
        
        if index == 2:
            return None
        
        if index < len(text) and text[index].upper() in 'LU':
            index += 1
        
        return index

    def shortId(self):
        return 'HlCHex()'

def _checkEscapedChar(text):
    index = 0
    if len(text) > 1 and text[0] == '\\':
        index = 1
        
        if text[index] in "abefnrtv'\"?\\":
            index += 1
        elif text[index] == 'x':  # if it's like \xff, eat the x
            index += 1
            while index < len(text) and text[index].upper() in '0123456789ABCDEF':
                index += 1
            if index == 2:  # no hex digits
                return None
        elif text[index] in '01234567':
            while index < 4 and index < len(text) and text[index] in '01234567':
                index += 1
        else:
            return None
        
        return index
    
    return None
    

class HlCStringChar(AbstractRule):
    def shortId(self):
        return 'HlCStringChar'

    def _tryMatchText(self, text, contextData):
        return _checkEscapedChar(text)


class HlCChar(AbstractRule):
    def shortId(self):
        return 'HlCChar'

    def _tryMatchText(self, text, contextData):
        if len(text) > 2 and text[0] == "'" and text[1] != "'":
            result = _checkEscapedChar(text[1:])
            if result is not None:
                index = 1 + result
            else:  # 1 not escaped character
                index = 1 + 1
            
            if index < len(text) and text[index] == "'":
                return index + 1
        
        return None


class RangeDetect(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._char = _safeGetRequiredAttribute(xmlElement, "char", 'char is not set')
        self._char1 = _safeGetRequiredAttribute(xmlElement, "char1", 'char1 is not set')
    
    def shortId(self):
        return 'RangeDetect(%s, %s)' % (self._char, self._char1)
    
    def _tryMatchText(self, text, contextData):
        if text.startswith(self._char):
            end = text.find(self._char1)
            if end > 0:
                return end + 1
        
        return None


class LineContinue(AbstractRule):
    def shortId(self):
        return 'LineContinue'

    def _tryMatchText(self, text, contextData):
        if text == '\\':
            return 1
        
        return None


class IncludeRules(AbstractRule):
    def __init__(self, parentContext, xmlElement):
        AbstractRule.__init__(self, parentContext, xmlElement)
        self._contextName = _safeGetRequiredAttribute(xmlElement, "context", None)
        # context will be resolved, when parsing. Avoiding infinite recursion

    def __str__(self):
        """Serialize.
        For debug logs
        """
        res = '\t\tRule %s\n' % self.shortId()
        res += '\t\t\tstyleName: %s\n' % self.attribute
        return res

    def shortId(self):
        return "IncludeRules(%s)" % self._contextName
    
    def _tryMatch(self, contextStack, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (count, matchedRule) or (None, None) if doesn't match
        """
        if self._contextName is not None:
            if self._contextName in self.parentContext.syntax.contexts:
                context = self.parentContext.syntax.contexts[self._contextName]
            elif self._contextName.startswith('##'):
                syntaxName = self._contextName[2:]
                syntax = self.parentContext.syntax.manager.getSyntaxByName(syntaxName)
                context = syntax.defaultContext
        else:
            context = self.parentContext.syntax.defaultContext
        
        for rule in context.rules:
            newContextStack, columnIndex, matchedRule = rule.tryMatch(contextStack, currentColumnIndex, text)
            if columnIndex is not None:
                return newContextStack, columnIndex, matchedRule
        else:
            return contextStack, None, None


class DetectSpaces(AbstractRule):
    def shortId(self):
        return 'DetectSpaces()'

    def _tryMatchText(self, text, contextData):
        spaceLen = len(text) - len(text.lstrip())
        if spaceLen:
            return spaceLen
        else:
            return None
        
class DetectIdentifier(AbstractRule):
    _regExp = re.compile('[a-zA-Z][a-zA-Z0-9]*')
    def shortId(self):
        return 'DetectIdentifier()'
    
    def _tryMatchText(self, text, contextData):
        match = DetectIdentifier._regExp.match(text)
        if match is not None and match.group(0):
            return len(match.group(0))
        
        return None


_ruleClasses = (DetectChar, Detect2Chars, AnyChar, StringDetect, WordDetect, RegExpr,
                keyword, Int, Float, HlCOct, HlCHex, HlCStringChar, HlCChar, RangeDetect,
                LineContinue, IncludeRules, DetectSpaces, DetectIdentifier)

ruleClassDict = {}
for ruleClass in _ruleClasses:
    ruleClassDict[ruleClass.__name__] = ruleClass

def _getChildRules(context, xmlElement):
    """Extract rules from Context or Rule xml element
    """
    rules = []
    for ruleElement in xmlElement.getchildren():
        if not ruleElement.tag in ruleClassDict:
            raise ValueError("Not supported rule '%s'" % ruleElement.tag)
        rule = ruleClassDict[ruleElement.tag](context, ruleElement)
        rules.append(rule)
    return rules
    

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
        self.rules = _getChildRules(self, self._xmlElement)

    
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
            res += unicode(rule)
        return res

    def parseBlock(self, contextStack, currentColumnIndex, text):
        """Parse block
        Exits, when reached end of the text, or when context is switched
        Returns (length, newContextStack, matchedRules)
        where matchedRules is:
            (Rule, pos, length)
        """
        startColumnIndex = currentColumnIndex
        matchedRules = []
        while currentColumnIndex < len(text):
            for rule in self.rules:
                newContextStack, count, matchedRule = rule.tryMatch(contextStack, currentColumnIndex, text)
                if count is not None:
                    matchedRules.append((matchedRule, currentColumnIndex, count))
                    currentColumnIndex += count
                    if newContextStack != contextStack:
                        return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)
                    
                    break  # for loop                    
            else:  # no matched rules
                if self.fallthroughContext is not None:
                    newContextStack = self.fallthroughContext.getNextContextStack(contextStack)
                    if newContextStack != contextStack:
                        return (currentColumnIndex - startColumnIndex, newContextStack, matchedRules)

                currentColumnIndex += 1

        return (currentColumnIndex - startColumnIndex, contextStack, matchedRules)

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

    def __init__(self, manager, filePath):
        """Parse XML definition
        """
        self.manager = manager
        with open(filePath, 'r') as definitionFile:
            root = xml.etree.ElementTree.parse(definitionFile).getroot()

        self.name = _safeGetRequiredAttribute(root, 'name', 'Error: Syntax name is not set!!!')
        
        self.section = _safeGetRequiredAttribute(root, 'section', 'Error: Section is not set!!!')
        self.extensions = _safeGetRequiredAttribute(root, 'extensions', '').split(';')
        
        self.mimetype = root.attrib.get('mimetype', '').split(';')
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
            # Sometimes item.text is none. Broken xml files
            items = [item.text.strip() \
                        for item in listElement.findall('item') \
                            if item.text is not None]
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
        res = u'Syntax %s\n' % self.name
        for name, value in vars(self).iteritems():
            if not name.startswith('_') and \
               not name in ('defaultContext', 'deliminatorSet', 'contexts', 'lists') and \
               not value is None:
                res += '\t%s: %s\n' % (name, value)
        
        res += '\tDefault context: %s\n' % self.defaultContext.name

        for listName, listValue in self.lists.iteritems():
            res += '\tList %s: %s\n' % (listName, listValue)
        
        
        for context in self.contexts.values():
            res += unicode(context)
        
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
            (lineData, [matchedContexts])
        where matchedContexts is:
            [ (Context, length, [matchedRules]), ...]
        where matchedRule is:
            (Rule, pos, length)
        """
        if prevLineData is not None:
            contextStack = prevLineData
        else:
            contextStack = _ContextStack.makeDefault(self)
        
        # this code is not tested, because lineBeginContext is not defined by any xml file
        if contextStack.currentContext().lineBeginContext is not None:
            contextStack = contextStack.currentContext().lineBeginContext.getNextContextStack(contextStack)
        
        matchedContexts = []
        
        currentColumnIndex = 0
        while currentColumnIndex < len(text):
            length, newContextStack, matchedRules = \
                        contextStack.currentContext().parseBlock(contextStack, currentColumnIndex, text)
            
            matchedContexts.append((contextStack.currentContext(), length, matchedRules))
            
            contextStack = newContextStack
            currentColumnIndex += length

        if contextStack.currentContext().lineEndContext is not None:
            contextStack = contextStack.currentContext().lineEndContext.getNextContextStack(contextStack)
        
        return contextStack, matchedContexts

    def parseBlockTextualResults(self, text, prevLineData=None):
        """Execute parseBlock() and return textual results.
        For debugging"""
        lineData, matchedContexts = self.parseBlock(text, prevLineData)
        lineDataTextual = [context.name for context in lineData._contexts]
        matchedContextsTextual = \
         [ (context.name, contextLength, [ (rule.shortId(), pos, length) \
                                                    for rule, pos, length in matchedRules]) \
                    for context, contextLength, matchedRules in matchedContexts]
        
        return matchedContextsTextual

    def _printParseBlockTextualResults(self, text, results):
        contextStart = 0
        for name, length, rules in results:
            print repr(text[contextStart:contextStart + length]), name
            contextStart += length
            for rule, pos, len in rules:
                print '\t', repr(text[pos: pos + len]), rule

    def parseAndPrintBlockTextualResults(self, text, prevLineData=None):
        res = self.parseBlockTextualResults(text, prevLineData)
        return self._printParseBlockTextualResults(text, res)
    
    def parseBlockContextStackTextual(self, text, prevLineData=None):
        """Execute parseBlock() and return context stack as list of context names
        For debugging"""
        lineData, matchedContexts = self.parseBlock(text, prevLineData)
        lineDataTextual = [context.name for context in lineData._contexts]
        
        return lineDataTextual
