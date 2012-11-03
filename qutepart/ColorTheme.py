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


class ColorTheme:
    """Color theme.
    """
    def __init__(self):
        self.format = {}
        self.format['dsNormal'] = TextFormat()
        self.format['dsKeyword'] = TextFormat(bold=True)
        self.format['dsDataType'] = TextFormat(color='#0057ae')
        self.format['dsDataType'] = TextFormat(color='#0057ae')
        self.format['dsDecVal'] = TextFormat(color='#b07e00')
        self.format['dsBaseN'] = TextFormat(color='#b07e00')
        self.format['dsFloat'] = TextFormat(color='#b07e00')
        self.format['dsChar'] = TextFormat(color='#ff80e0')
        self.format['dsString'] = TextFormat(color='#bf0303')
        self.format['dsComment'] = TextFormat(color='#888786', italic=True)
        self.format['dsOthers'] = TextFormat(color='#006e26')
        self.format['dsAlert'] = TextFormat(color='#bf0303', background='#f7e7e7', bold=True)
        self.format['dsFunction'] = TextFormat(color='#442886')
        self.format['dsRegionMarker'] = TextFormat(color='#0057ae', background='#e1eaf8')
        self.format['dsError'] = TextFormat(color='#bf0303', underline=True)
    
    def getFormat(self, styleName):
        """Returns TextFormat for particular style
        """
        return self.format[styleName]
