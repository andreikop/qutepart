from PyQt4.QtGui import QBrush, QColor, QFont, QTextCharFormat


class ColorTheme:
    """Color theme.
    """
    _DEFAULT_STYLE_NAMES = \
     ("dsNormal",
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
      "dsError")
    def __init__(self):
        
        self._format = {}
        for format in ColorTheme._DEFAULT_STYLE_NAMES:
            self._format[format] = QTextCharFormat()
        
        self._format['dsKeyword'].setFontWeight(QFont.Bold)
        
        self._format['dsDataType'].setForeground(QBrush(QColor('#0057ae')))
        
        self._format['dsDecVal'].setForeground(QBrush(QColor('#b07e00')))
        self._format['dsBaseN'].setForeground(QBrush(QColor('#b07e00')))
        self._format['dsFloat'].setForeground(QBrush(QColor('#b07e00')))
        
        self._format['dsChar'].setForeground(QBrush(QColor('#ff80e0')))
        
        self._format['dsString'].setForeground(QBrush(QColor('#bf0303')))
        
        self._format['dsComment'].setForeground(QBrush(QColor('#888786')))
        self._format['dsComment'].setFontItalic(True)
        
        self._format['dsOthers'].setForeground(QBrush(QColor('#006e26')))
        
        self._format['dsAlert'].setForeground(QBrush(QColor('#bf0303')))
        self._format['dsAlert'].setFontWeight(QFont.Bold)
        self._format['dsAlert'].setBackground(QBrush(QColor('#f7e7e7')))
        
        self._format['dsFunction'].setForeground(QBrush(QColor('#442886')))
        
        self._format['dsRegionMarker'].setForeground(QBrush(QColor('#0057ae')))
        
        self._format['dsError'].setForeground(QBrush(QColor('#e1eaf8')))
    
    def getFormat(self, styleName):
        """Returns QTextCharFormat for particular style
        """
        return self._format[styleName]
