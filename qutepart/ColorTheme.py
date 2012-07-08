from PyQt4.QtGui import QBrush, QColor, QFont, QTextCharFormat


class ColorTheme:
    """Color theme.
    """
    _COMMON_FORMAT = ("Normal",
                      "Keyword",
                      "DataType",
                      "DecVal",
                      "BaseN",
                      "Float",
                      "Char",
                      "String",
                      "Comment",
                      "Others",
                      "Alert",
                      "Function",
                      "RegionMarker",
                      "Error")
    def __init__(self):
        
        self._format = {}
        for format in ColorTheme._COMMON_FORMAT:
            self._format[format] = QTextCharFormat()
        
        self._format['Keyword'].setFontWeight(QFont.Bold)
        
        self._format['DataType'].setForeground(QBrush(QColor('#0057ae')))
        
        self._format['DecVal'].setForeground(QBrush(QColor('#b07e00')))
        self._format['BaseN'].setForeground(QBrush(QColor('#b07e00')))
        self._format['Float'].setForeground(QBrush(QColor('#b07e00')))
        
        self._format['Char'].setForeground(QBrush(QColor('#ff80e0')))
        
        self._format['String'].setForeground(QBrush(QColor('#bf0303')))
        
        self._format['Comment'].setForeground(QBrush(QColor('#888786')))
        self._format['Comment'].setFontItalic(True)
        
        self._format['Others'].setForeground(QBrush(QColor('#006e26')))
        
        self._format['Alert'].setForeground(QBrush(QColor('#bf0303')))
        self._format['Alert'].setFontWeight(QFont.Bold)
        self._format['Alert'].setBackground(QBrush(QColor('#f7e7e7')))
        
        self._format['Function'].setForeground(QBrush(QColor('#442886')))
        
        self._format['RegionMarker'].setForeground(QBrush(QColor('#0057ae')))
        
        self._format['Error'].setForeground(QBrush(QColor('#e1eaf8')))
    
    def getFormat(self, formatName):
        """Returns QTextCharFormat for particular style
        """
        return self._format[formatName]
