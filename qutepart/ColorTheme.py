class TextFormat:
    """Text format definition.
    
    Public attributes:
        color          : Font color, #rrggbb
        background     : Font background, #rrggbb
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


class ColorTheme:
    """Color theme.
    """
    def __init__(self):
        self._format = {}
        self._format['dsNormal'] = TextFormat()
        self._format['dsKeyword'] = TextFormat(bold=True)
        self._format['dsDataType'] = TextFormat(color='#0057ae')
        self._format['dsDataType'] = TextFormat(color='#0057ae')
        self._format['dsDecVal'] = TextFormat(color='#b07e00')
        self._format['dsBaseN'] = TextFormat(color='#b07e00')
        self._format['dsFloat'] = TextFormat(color='#b07e00')
        self._format['dsChar'] = TextFormat(color='#ff80e0')
        self._format['dsString'] = TextFormat(color='#bf0303')
        self._format['dsComment'] = TextFormat(color='#888786', italic=True)
        self._format['dsOthers'] = TextFormat(color='#006e26')
        self._format['dsAlert'] = TextFormat(color='#bf0303', background='#f7e7e7', bold=True)
        self._format['dsFunction'] = TextFormat(color='#442886')
        self._format['dsRegionMarker'] = TextFormat(color='#0057ae')
        self._format['dsError'] = TextFormat(color='#e1eaf8')
    
    def getFormat(self, styleName):
        """Returns QTextCharFormat for particular style
        """
        return self._format[styleName]
