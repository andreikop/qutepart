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
    Public attributes:
        parentContext
        attribute
        context
        lookAhead
        firstNonSpace
        column
        dynamic
    """
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
    """Public attributes:
        char
    """
    def shortId(self):
        return 'DetectChar(%s)' % self.char
    
    def _tryMatchText(self, text, contextData):
        if self.char is None:
            return None

        if self.dynamic:
            index = int(self.char) - 1
            if index >= len(contextData):
                print >> sys.stderr, 'Invalid DetectChar index', index
                return None
            
            if len(contextData[index]) != 1:
                    print >> sys.stderr, 'Too long DetectChar string', contextData[index]
                    return None
            
            string = contextData[index]
        else:
            string = self.char
        
        if text[0] == string:
            return 1
        return None

class Detect2Chars(AbstractRule):
    """Public attributes
        string
    """
    def shortId(self):
        return 'Detect2Chars(%s)' % self.string
    
    def _tryMatchText(self, text, contextData):
        if self.string is None:
            return None
        
        if text.startswith(self.string):
            return len(self.string)
        
        return None


class AnyChar(AbstractRule):
    """Public attributes:
        string
    """
    def shortId(self):
        return 'AnyChar(%s)' % self.string
    
    def _tryMatchText(self, text, contextData):
        if text[0] in self.string:
            return 1
        
        return None


class StringDetect(AbstractRule):
    """Public attributes:
        string
    """
    def shortId(self):
        return 'StringDetect(%s)' % self.string

    def _tryMatchText(self, text, contextData):
        if self.string is None:
            return
        
        if self.dynamic:
            string = self._makeDynamicStringSubsctitutions(self.string)
        else:
            string = self.string
        
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
        
        for word in self.words:
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
    """Public attributes:
        words
    """
    def shortId(self):
        return 'WordDetect(%s, %s)' % (' '.join(self.words), self._insensitive)

class keyword(AbstractWordRule):
    """Public attributes:
        string
        words
    """
    def shortId(self):
        return 'keyword(%s)' % repr(self.string)


class RegExpr(AbstractRule):
    """TODO if regexp starts with ^ - match only column 0
    TODO support "minimal" flag
    
    Public attributes:
        regExp
    """
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
        return 'RegExpr(%s)' % self.string

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
            string = self._makeDynamicStringSubsctitutions(self.string, contextStack.currentData())
            regExp = self._compileRegExp(string, self._insensitive)
        else:
            regExp = self.regExp
        
        if regExp is None:
            return None
        
        match = regExp.match(text[currentColumnIndex:])
        if match is not None and match.group(0):
            print self.string, regExp.pattern, match.groups()
            count = len(match.group(0))

            if self.context is not None:
                contextStack = self.context.getNextContextStack(contextStack, match.groups())
            return contextStack, count, self
        else:
            return contextStack, None, None


class AbstractNumberRule(AbstractRule):
    """Base class for Int and Float rules.
    This rules can have child rules
    
    Public attributes:
        childRules
    """
    def _tryMatch(self, contextStack, currentColumnIndex, text):
        """Try to find themselves in the text.
        Returns (count, matchedRule) or (None, None) if doesn't match
        """        
        index = self._tryMatchText(text[currentColumnIndex:], contextStack.currentData())
        if index is None:
            return contextStack, None, None
        
        if currentColumnIndex + index < len(text):
            for rule in self.childRules:
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
    """Public attributes:
        char
        char1
    """
    def shortId(self):
        return 'RangeDetect(%s, %s)' % (self.char, self.char1)
    
    def _tryMatchText(self, text, contextData):
        if text.startswith(self.char):
            end = text.find(self.char1)
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

class Context:
    """Highlighting context
    
    Public attributes:
        attribute
        lineEndContext
        lineBeginContext
        fallthroughContext
        dynamic
        rules
    """
    def __init__(self, syntax, name):
        # Will be initialized later, after all context has been created
        self.syntax = syntax
        self.name = name
    
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
    
    Informative public attributes:
        name            Name
        section         Section
        extensions      File extensions
        mimetype        File mime type
        version         XML definition version
        kateversion     Required Kate parser version
        priority        XML definition priority
        author          Author
        license         License
        hidden          Shall be hidden in the menu
        
    Effective public attributes:
        deliminatorSet          Set of deliminator characters
        lists                   Keyword lists as dictionary "list name" : "list value"
        defaultContext          Default context object
        contexts                Context list as dictionary "context name" : context
        attributeToStyleMap     Map "attribute" : "style name"   
    """
        
    def __init__(self, manager):
        """Parse XML definition
        """
        self.manager = manager
        
        # Other attributes are initialized by the XML loader

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
        if not attribute.lower() in self.attributeToStyleMap:
            print >> sys.stderr, "Unknown attribute '%s'" % attribute
            return self.attributeToStyleMap['normal']
        
        # attribute names are not case sensetive
        return self.attributeToStyleMap[attribute.lower()]

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
