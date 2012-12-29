"""Default color theme
"""

class ColorTheme:
    """Color theme.
    """
    def __init__(self, textFormatClass):
        """Constructor gets TextFormat class as parameter for avoid cross-import problems
        """
        self.format = {}
        self.format['dsNormal'] = textFormatClass()
        self.format['dsKeyword'] = textFormatClass(bold=True)
        self.format['dsDataType'] = textFormatClass(color='#0057ae')
        self.format['dsDataType'] = textFormatClass(color='#0057ae')
        self.format['dsDecVal'] = textFormatClass(color='#b07e00')
        self.format['dsBaseN'] = textFormatClass(color='#b07e00')
        self.format['dsFloat'] = textFormatClass(color='#b07e00')
        self.format['dsChar'] = textFormatClass(color='#ff80e0')
        self.format['dsString'] = textFormatClass(color='#bf0303')
        self.format['dsComment'] = textFormatClass(color='#888786', italic=True)
        self.format['dsOthers'] = textFormatClass(color='#006e26')
        self.format['dsAlert'] = textFormatClass(color='#bf0303', background='#f7e7e7', bold=True)
        self.format['dsFunction'] = textFormatClass(color='#442886')
        self.format['dsRegionMarker'] = textFormatClass(color='#0057ae', background='#e1eaf8')
        self.format['dsError'] = textFormatClass(color='#bf0303', underline=True)
    
    def getFormat(self, styleName):
        """Returns TextFormat for particular style
        """
        return self.format[styleName]
