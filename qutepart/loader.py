import copy
import sys
import xml.etree.ElementTree


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

_DEFAULT_DELIMINATOR = " \t.():!+,-<=>%&*/;?[]^{|}~\\"


def _parseBoolAttribute(value):
    if value.lower() in ('true', '1'):
        return True
    elif value.lower() in ('false', '0'):
        return False
    else:
        raise UserWarning("Invalid bool attribute value '%s'" % value)

def _safeGetRequiredAttribute(xmlElement, name, default):
    if name in xmlElement.attrib:
        return xmlElement.attrib[name]
    else:
        print >> sys.stderr, "Required attribute '%s' is not set for element '%s'" % (name, xmlElement.tag)
        return default


def _loadAttributeToStyleMap(highlightingElement):
    attributeToStyleMap = copy.copy(_DEFAULT_ATTRIBUTE_TO_STYLE_MAP)

    itemDatasElement = highlightingElement.find('itemDatas')
    for item in itemDatasElement.findall('itemData'):
        name, styleName = item.get('name'), item.get('defStyleNum')
        
        if styleName is None:  # custom format
            styleName = 'CustomTmpForDebugging'
        
        if not styleName in _KNOWN_STYLES:
            print >> sys.stderr, "Unknown default style '%s'" % styleName
            styleName = 'dsNormal'
        name = name.lower()  # format names are not case sensetive
        attributeToStyleMap[name] = styleName
    
    return attributeToStyleMap

def _loadContexts(highlightingElement, syntax):
    from Syntax import Context  # FIXME
    contexts = {}
    
    contextsElement = highlightingElement.find('contexts')
    firstContext = True
    
    for contextElement in contextsElement.findall('context'):
        context = Context(syntax, contextElement)
        contexts[context.name] = context
        if firstContext:
            firstContext = False
            syntax.defaultContext = context
    
    syntax.contexts = contexts  # FIXME
    
    # parse contexts stage 2: load contexts
    for context in contexts.values():
        context.load()

    return contexts

def _loadLists(root, highlightingElement):
    lists = {}  # list name: list
    for listElement in highlightingElement.findall('list'):
        # Sometimes item.text is none. Broken xml files
        items = [item.text.strip() \
                    for item in listElement.findall('item') \
                        if item.text is not None]
        name = _safeGetRequiredAttribute(listElement, 'name', 'Error: list name is not set!!!')
        lists[name] = items
    
    casesensitive = _parseBoolAttribute(root.attrib.get('casesensitive', 'true'))
    # Make all keywords lowercase, if syntax is not case sensetive
    if not casesensitive:
        for keywordList in lists.values():
            for index, keyword in enumerate(keywordList):
                keywordList[index] = keyword.lower()

    return lists

def loadSyntax(manager, filePath):
    from Syntax import Syntax  # FIXME
    
    syntax = Syntax(manager)
    
    with open(filePath, 'r') as definitionFile:
        root = xml.etree.ElementTree.parse(definitionFile).getroot()

    syntax.name = _safeGetRequiredAttribute(root, 'name', 'Error: Syntax name is not set!!!')
    
    syntax.section = _safeGetRequiredAttribute(root, 'section', 'Error: Section is not set!!!')
    syntax.extensions = _safeGetRequiredAttribute(root, 'extensions', '').split(';')
    
    syntax.mimetype = root.attrib.get('mimetype', '').split(';')
    syntax.version = root.attrib.get('version', None)
    syntax.kateversion = root.attrib.get('kateversion', None)
    
    syntax.priority = root.attrib.get('priority', None)
    syntax.author = root.attrib.get('author', None)
    syntax.license = root.attrib.get('license', None)
    
    syntax.hidden = _parseBoolAttribute(root.attrib.get('hidden', 'false'))
    
    syntax.deliminatorSet = set(_DEFAULT_DELIMINATOR)
    
    highlightingElement = root.find('highlighting')
    
    # parse lists
    syntax.lists = _loadLists(root, highlightingElement)
    
    # parse itemData
    syntax.attributeToStyleMap = _loadAttributeToStyleMap(highlightingElement)
    
    # parse contexts stage 1: create objects
    syntax.contexts = _loadContexts(highlightingElement, syntax)

    return syntax
