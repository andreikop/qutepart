"""This module manages knows file => parser class associations and 
holds already created Parser instances
Use this module for getting Parser'es
"""

import os.path
import fnmatch
import json

import qutepart.parser
import qutepart.loader

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
        spellChecking  : Striked out font
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


class HighlightedSegment:
    def __init__(self, length, format):
        self.length = length
        self.format = format


class ParseBlockResult:
    def __init__(self, parseBlockFullResult):
        self.lineData = parseBlockFullResult.lineData
        
        self.highlightedSegments = []
        
        currentPos = 0
        for matchedContext in parseBlockFullResult.matchedContexts:
            matchedCntextStartPos = currentPos
            for matchedRule in matchedContext.matchedRules:
                if matchedRule.pos > currentPos:
                    self._appendHighlightedSegment(matchedRule.pos - currentPos,
                                                   matchedContext.context.format)
                self._appendHighlightedSegment(matchedRule.length,
                                               matchedRule.rule.format)
                currentPos = matchedRule.pos + matchedRule.length
            if currentPos < matchedCntextStartPos + matchedContext.length:
                self._appendHighlightedSegment(matchedCntextStartPos + matchedContext.length - currentPos,
                                               matchedContext.context.format)

    def _appendHighlightedSegment(self, length, format):
        self.highlightedSegments.append(HighlightedSegment(length, format))


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
    """
    def __init__(self, manager):
        self.manager = manager
    
    def parseBlock(self, text, prevLineData):
        return self.parser.parseBlock(text, prevLineData)

class SyntaxManager:
    def __init__(self):
        self._loadedSyntaxes = {}
        syntaxDbPath = os.path.join(os.path.dirname(__file__), "syntax", "syntax_db.json")
        with open(syntaxDbPath) as syntaxDbFile:
            syntaxDb = json.load(syntaxDbFile)
        self._syntaxNameToXmlFileName = syntaxDb['syntaxNameToXmlFileName']
        self._mimeTypeToXmlFileName = syntaxDb['mimeTypeToXmlFileName']
        self._extensionToXmlFileName = syntaxDb['extensionToXmlFileName']

    def getSyntaxByXmlName(self, xmlFileName):
        if not xmlFileName in self._loadedSyntaxes:
            xmlFilePath = os.path.join(os.path.dirname(__file__), "syntax", xmlFileName)
            syntax = Syntax(self)
            self._loadedSyntaxes[xmlFileName] = syntax
            qutepart.loader.loadSyntax(syntax, xmlFilePath)
        
        return self._loadedSyntaxes[xmlFileName]

    def getSyntaxByName(self, syntaxName):
        xmlFileName = self._syntaxNameToXmlFileName[syntaxName]
        return self.getSyntaxByXmlName(xmlFileName)
    
    def getSyntaxBySourceFileName(self, name):
        for pattern, xmlFileName in self._extensionToXmlFileName.items():
            if fnmatch.fnmatch(name, pattern):
                return self.getSyntaxByXmlName(xmlFileName)
        else:
            raise KeyError("No syntax for " + name)

    def getSyntaxByMimeType(self, mimeType):
        xmlFileName = self._mimeTypeToXmlFileName[mimeType]
        return self.getSyntaxByXmlName(xmlFileName)
