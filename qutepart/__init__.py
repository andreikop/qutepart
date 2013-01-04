"""Code editor component for PyQt and Pyside

Use Qutepart class as an API
"""

import os.path

from PyQt4.QtGui import QFont, QPlainTextEdit

from qutepart.syntax import SyntaxManager
from qutepart.highlighter import SyntaxHighlighter

class Qutepart(QPlainTextEdit):
    """Code editor component for PyQt and Pyside
    """
    
    _globalSyntaxManager = SyntaxManager()
    
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        
        self._highlighter = None
        
        self.setFont(QFont("Monospace"))
    
    def detectSyntax(self, xmlFileName = None, mimeType = None, languageName = None, sourceFilePath = None):
        """Get syntax by one of parameters:
            * xmlFileName
            * mimeType
            * languageName
            * sourceFilePath
        First parameter in the list has biggest priority.
        Old syntax is always cleared, even if failed to detect new.
        
        Method returns True, if syntax is detected, and False otherwise
        """
        self.clearSyntax()
        
        syntax = self._globalSyntaxManager.getSyntax(SyntaxHighlighter.formatConverterFunction,
                                                     xmlFileName = xmlFileName,
                                                     mimeType = mimeType,
                                                     languageName = languageName,
                                                     sourceFilePath = sourceFilePath)

        if syntax is not None:
            self._highlighter = SyntaxHighlighter(syntax, self.document())

    def clearSyntax(self):
        """Clear syntax. Disables syntax highlighting
        
        This method might take long time, if document is big. Don't call it if you don't have to.
        """
        if self._highlighter is not None:
            self._highlighter.del_()
            self._highlighter = None
