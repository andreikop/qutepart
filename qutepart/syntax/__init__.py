"""Source file parser and highlighter
"""

import os.path
import fnmatch
import json
import threading
import logging

_logger = logging.getLogger('qutepart')

class TextFormat:
    """Text format definition.
    
    Public attributes:
        color          : Font color, #rrggbb or #rgb
        background     : Font background, #rrggbb or #rgb
        selectionColor : Color of selected text
        italic         : Italic font, bool
        bold           : Bold font, bool
        underline      : Underlined font, bool
        strikeOut      : Striked out font
        spellChecking  : Text will be spell checked
        textType       : 'c' for comments, 's' for strings, ' ' for other. 
    """
    def __init__(self, color = '#000000',
                       background = '#ffffff',
                       selectionColor = '#0000ff',
                       italic = False,
                       bold = False,
                       underline = False,
                       strikeOut = False,
                       spellChecking = False):
        
        self.color = color
        self.background = background
        self.selectionColor = selectionColor
        self.italic = italic
        self.bold = bold
        self.underline = underline
        self.strikeOut = strikeOut
        self.spellChecking = spellChecking
        self.textType = ' '  # modified later


class Syntax:
    """Syntax. Programming language parser definition
    
    Public attributes:
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
        indenter        Indenter for the syntax. Possible values are 
                            none, normal, cstyle, haskell, lilypond, lisp, python, ruby, xml
                        None, if not set by xml file
    """
    def __init__(self, manager):
        self.manager = manager
        self.parser = None
    
    def __str__(self):
        res = 'Syntax\n'
        res += ' name: %s\n' % self.name
        res += ' section: %s\n' % self.section
        res += ' extensions: %s\n' % self.extensions
        res += ' mimetype: %s\n' % self.mimetype
        res += ' version: %s\n' % self.version
        res += ' kateversion: %s\n' % self.kateversion
        res += ' priority: %s\n' % self.priority
        res += ' author: %s\n' % self.author
        res += ' license: %s\n' % self.license
        res += ' hidden: %s\n' % self.hidden
        res += ' indenter: %s\n' % self.indenter
        res += unicode(self.parser)
        
        return res
    
    def _setParser(self, parser):
        self.parser = parser
        # performance optimization, avoid 1 function call
        self.highlightBlock = parser.highlightBlock
        self.parseBlock = parser.parseBlock
    
    def highlightBlock(self, text, prevLineData):
        """Parse line of text and return
            (lineData, highlightedSegments)
        where
            lineData is data, which shall be saved and used for parsing next line
            highlightedSegments is list of touples (segmentLength, segmentFormat)
        """
        #self.parser.parseAndPrintBlockTextualResults(text, prevLineData)
        return self.parser.highlightBlock(text, prevLineData)
        
    def parseBlock(self, text, prevLineData):
        """Parse line of text and return
            lineData
        where
            lineData is data, which shall be saved and used for parsing next line
            
        This is quicker version of highlighBlock, which doesn't return results,
        but only parsers the block and produces data, which is necessary for parsing next line.
        Use it for invisible lines
        """
        return self.parser.parseBlock(text, prevLineData)
    
    def isCode(self, lineData, column):
        """Check if text at given position is a code
        """
        return lineData is None or \
               lineData[1][column] == ' '

    def isComment(self, lineData, column):
        """Check if text at given position is a comment
        """
        return lineData is not None and \
               lineData[1][column] == 'c'

class SyntaxManager:
    """SyntaxManager holds references to loaded Syntax'es and allows to find or
    load Syntax by its name or by source file name
    """
    def __init__(self):
        self._loadedSyntaxesLock = threading.RLock()
        self._loadedSyntaxes = {}
        syntaxDbPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), "data", "syntax_db.json")
        with open(syntaxDbPath) as syntaxDbFile:
            syntaxDb = json.load(syntaxDbFile)
        self._syntaxNameToXmlFileName = syntaxDb['syntaxNameToXmlFileName']
        self._mimeTypeToXmlFileName = syntaxDb['mimeTypeToXmlFileName']
        self._extensionToXmlFileName = syntaxDb['extensionToXmlFileName']

    def _getSyntaxByXmlFileName(self, xmlFileName, formatConverterFunction):
        """Get Syntax by its xml file name
        """
        import qutepart.syntax.loader  # delayed import for avoid cross-imports problem
        
        with self._loadedSyntaxesLock:
            if not xmlFileName in self._loadedSyntaxes:
                xmlFilePath = os.path.join(os.path.dirname(__file__), "data", xmlFileName)
                syntax = Syntax(self)
                self._loadedSyntaxes[xmlFileName] = syntax
                qutepart.syntax.loader.loadSyntax(syntax, xmlFilePath, formatConverterFunction)
        
            return self._loadedSyntaxes[xmlFileName]

    def _getSyntaxByLanguageName(self, syntaxName, formatConverterFunction):
        """Get syntax by its name. Name is defined in the xml file
        """
        xmlFileName = self._syntaxNameToXmlFileName[syntaxName]
        return self._getSyntaxByXmlFileName(xmlFileName, formatConverterFunction)
    
    def _getSyntaxBySourceFileName(self, name, formatConverterFunction):
        """Get Syntax by source name of file, which is going to be highlighted
        """
        for pattern, xmlFileName in self._extensionToXmlFileName.items():
            if fnmatch.fnmatch(name, pattern):
                return self._getSyntaxByXmlFileName(xmlFileName, formatConverterFunction)
        else:
            raise KeyError("No syntax for " + name)

    def _getSyntaxByMimeType(self, mimeType, formatConverterFunction):
        """Get Syntax by file mime type
        """
        xmlFileName = self._mimeTypeToXmlFileName[mimeType]
        return self._getSyntaxByXmlFileName(xmlFileName, formatConverterFunction)

    def getSyntax(self, formatConverterFunction = None,
                  xmlFileName = None, mimeType = None, languageName = None, sourceFilePath = None):
        """Get syntax by one of parameters:
            * xmlFileName
            * mimeType
            * languageName
            * sourceFilePath
        First parameter in the list has biggest priority
        """
        syntax = None
        
        if syntax is None and xmlFileName is not None:
            try:
                syntax = self._getSyntaxByXmlFileName(xmlFileName, formatConverterFunction)
            except KeyError:
                _logger.warning('No xml definition %s' % xmlFileName)
        
        if syntax is None and mimeType is not None:
            try:
                syntax = self._getSyntaxByMimeType(mimeType, formatConverterFunction)
            except KeyError:
                _logger.warning('No syntax for mime type %s' % mimeType)
        
        if syntax is None and languageName is not None:
            try:
                syntax = self._getSyntaxByLanguageName(languageName, formatConverterFunction)
            except KeyError:
                _logger.warning('No syntax for language %s' % languageName)
        
        if syntax is None and sourceFilePath is not None:
            baseName = os.path.basename(sourceFilePath)
            try:
                syntax = self._getSyntaxBySourceFileName(baseName, formatConverterFunction)
            except KeyError:
                pass

        return syntax
