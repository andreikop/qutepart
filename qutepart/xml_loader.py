import copy
import sys

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

def loadStyleNameMap(highlightingElement):
    styleNameMap = copy.copy(_DEFAULT_ATTRIBUTE_TO_STYLE_MAP)

    itemDatasElement = highlightingElement.find('itemDatas')
    for item in itemDatasElement.findall('itemData'):
        name, styleName = item.get('name'), item.get('defStyleNum')
        
        if styleName is None:  # custom format
            styleName = 'CustomTmpForDebugging'
        
        if not styleName in _KNOWN_STYLES:
            print >> sys.stderr, "Unknown default style '%s'" % styleName
            styleName = 'dsNormal'
        name = name.lower()  # format names are not case sensetive
        styleNameMap[name] = styleName
    
    return styleNameMap
