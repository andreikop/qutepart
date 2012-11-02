import copy
import sys
import xml.etree.ElementTree

from qutepart.Syntax import *
from qutepart.ColorTheme import ColorTheme, TextFormat


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

################################################################################
##                               Rules
################################################################################

def _loadIncludeRules(parentContext, xmlElement):
    rule = IncludeRules()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    rule._contextName = _safeGetRequiredAttribute(xmlElement, "context", None)
    # context will be resolved, when parsing. Avoiding infinite recursion
    return rule

def _simpleLoader(classObject):
    def _load(parentContext, xmlElement):
        rule = classObject()
        _loadAbstractRule(rule, parentContext, xmlElement)
        return rule
    return _load

def _loadChildRules(context, xmlElement):
    """Extract rules from Context or Rule xml element
    """
    rules = []
    for ruleElement in xmlElement.getchildren():
        if not ruleElement.tag in _ruleClassDict:
            raise ValueError("Not supported rule '%s'" % ruleElement.tag)
        rule = _ruleClassDict[ruleElement.tag](context, ruleElement)
        rules.append(rule)
    return rules

def _loadAbstractRule(rule, parentContext, xmlElement):
    import Syntax  # FIXME
    rule.parentContext = parentContext

    # attribute
    rule.attribute = xmlElement.attrib.get("attribute", None)
    if not rule.attribute is None:
        rule.attribute = rule.attribute.lower()  # not case sensetive
        try:
            rule.format = parentContext.syntax.attributeToFormatMap[rule.attribute]
        except KeyError:
            print >> sys.stderr, 'Unknown rule attribute', rule.attribute
            rule.format = TextFormat()

    # context
    contextText = xmlElement.attrib.get("context", '#stay')
    rule.context = ContextSwitcher(contextText, parentContext.syntax.contexts)

    rule.lookAhead = _parseBoolAttribute(xmlElement.attrib.get("lookAhead", "false"))
    rule.firstNonSpace = _parseBoolAttribute(xmlElement.attrib.get("firstNonSpace", "false"))
    rule.dynamic = _parseBoolAttribute(xmlElement.attrib.get("dynamic", "false"))
    
    # TODO beginRegion
    # TODO endRegion
    
    column = xmlElement.attrib.get("column", None)
    if column is not None:
        rule.column = int(column)
    else:
        rule.column = None

def _loadDetectChar(parentContext, xmlElement):
    rule = DetectChar()
    _loadAbstractRule(rule, parentContext, xmlElement)
    rule.char = _safeGetRequiredAttribute(xmlElement, "char", None)
    
    if rule.dynamic:
        try:
            index = int(rule.char)
        except ValueError:
            print >> sys.stderr, 'Invalid DetectChar char', rule.char
            rule.char = None
        if index <= 0:
            print >> sys.stderr, 'Too little DetectChar index', rule.char
            rule.char = None
    
    return rule

def _loadDetect2Chars(parentContext, xmlElement):
    rule = Detect2Chars()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    char = _safeGetRequiredAttribute(xmlElement, 'char', None)
    char1 = _safeGetRequiredAttribute(xmlElement, 'char1', None)
    if char is None or char1 is None:
        rule.string = None
    else:
        rule.string = char + char1
    
    return rule

def _loadAnyChar(parentContext, xmlElement):
    rule = AnyChar()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    rule.string = _safeGetRequiredAttribute(xmlElement, 'String', '')
    return rule

def _loadStringDetect(parentContext, xmlElement):
    rule = StringDetect()
    _loadAbstractRule(rule, parentContext, xmlElement)
    rule.string = _safeGetRequiredAttribute(xmlElement, 'String', None)
    return rule

def _loadWordDetect(parentContext, xmlElement):
    rule = WordDetect()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    rule.words = [_safeGetRequiredAttribute(xmlElement, "String", "")]
    
    rule.insensitive = _parseBoolAttribute(xmlElement.attrib.get("insensitive", "false"))
    return rule

def _loadKeyword(parentContext, xmlElement):
    rule = keyword()
    _loadAbstractRule(rule, parentContext, xmlElement)
    rule.string = _safeGetRequiredAttribute(xmlElement, 'String', None)
    try:
        rule.words = rule.parentContext.syntax.lists[rule.string]
    except KeyError:
        print >> sys.stderr, 'List', rule.string, 'not found'
        rule.words = []
    
    rule.insensitive = _parseBoolAttribute(xmlElement.attrib.get("insensitive", "false"))
    return rule

def _loadRegExpr(parentContext, xmlElement):
    def _processCraracterCodes(text):
        """QRegExp use \0ddd notation for character codes, where d in octal digit
        i.e. \0377 is character with code 255 in the unicode table
        Convert such notation to unicode text
        """
        text = unicode(text)
        def replFunc(matchObj):
            matchText = matchObj.group(0)
            charCode = eval(matchText[1:])
            return chr(charCode).decode('latin1')
        return re.sub(r"\\0\d\d\d", replFunc, text)

    rule = RegExpr()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    string = _safeGetRequiredAttribute(xmlElement, 'String', None)        

    if string is None:
        rule.regExp = None
        return
        
    rule.string = _processCraracterCodes(string)
    rule.insensitive = xmlElement.attrib.get('insensitive', False)
    
    if not rule.dynamic:
        rule.regExp = rule._compileRegExp(rule.string, rule.insensitive)
    
    return rule

def _loadAbstractNumberRule(rule, parentContext, xmlElement):
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    rule.childRules = _loadChildRules(parentContext, xmlElement)

def _loadInt(parentContext, xmlElement):
    rule = Int()
    _loadAbstractNumberRule(rule, parentContext, xmlElement)
    return rule

def _loadFloat(parentContext, xmlElement):
    rule = Float()
    _loadAbstractNumberRule(rule, parentContext, xmlElement)
    return rule

def _loadRangeDetect(parentContext, xmlElement):
    rule = RangeDetect()
    _loadAbstractRule(rule, parentContext, xmlElement)
    
    rule.char = _safeGetRequiredAttribute(xmlElement, "char", 'char is not set')
    rule.char1 = _safeGetRequiredAttribute(xmlElement, "char1", 'char1 is not set')
    return rule


_ruleClassDict = \
{
    'DetectChar': _loadDetectChar,
    'Detect2Chars': _loadDetect2Chars,
    'AnyChar': _loadAnyChar,
    'StringDetect': _loadStringDetect,
    'WordDetect': _loadWordDetect,
    'RegExpr': _loadRegExpr,
    'keyword': _loadKeyword,
    'Int': _loadInt,
    'Float': _loadFloat,
    'HlCOct': _simpleLoader(HlCOct),
    'HlCHex': _simpleLoader(HlCHex),
    'HlCStringChar': _simpleLoader(HlCStringChar),
    'HlCChar': _simpleLoader(HlCChar),
    'RangeDetect': _loadRangeDetect,
    'LineContinue': _simpleLoader(LineContinue),
    'IncludeRules': _loadIncludeRules,
    'DetectSpaces': _simpleLoader(DetectSpaces),
    'DetectIdentifier': _simpleLoader(DetectIdentifier)
}

################################################################################
##                               Context
################################################################################


def _loadContexts(highlightingElement, syntax):
    from Syntax import Context  # FIXME
    
    contextsElement = highlightingElement.find('contexts')
    
    xmlElementList = contextsElement.findall('context')
    contextList = []
    for xmlElement in xmlElementList:
        name = _safeGetRequiredAttribute(xmlElement,
                                         'name',
                                         'Error: context name is not set!!!')
        context = Context(syntax, name)
        contextList.append(context)

    syntax.defaultContext = contextList[0]
    
    contextDict = {}
    for context in contextList:
        contextDict[context.name] = context
    
    syntax.contexts = contextDict  # FIXME
    
    # parse contexts stage 2: load contexts
    for xmlElement, context in zip(xmlElementList, contextList):
        _loadContext(context, xmlElement)

def _loadContext(context, xmlElement):
    """Construct context from XML element
    Contexts are at first constructed, and only then loaded, because when loading context,
    ContextSwitcher must have references to all defined contexts
    """
    context.attribute = _safeGetRequiredAttribute(xmlElement, 'attribute', '<not set>').lower()
    if context.attribute != '<not set>':  # there are no attributes for internal contexts, used by rules. See perl.xml
        try:
            context.format = context.syntax.attributeToFormatMap[context.attribute]
        except KeyError:
            print >> sys.stderr, 'Unknown context attribute', context.attribute
            context.format = TextFormat()
    else:
        context.format = None
    
    lineEndContextText = xmlElement.attrib.get('lineEndContext', '#stay')
    context.lineEndContext = ContextSwitcher(lineEndContextText,  context.syntax.contexts)
    lineBeginContextText = xmlElement.attrib.get('lineEndContext', '#stay')
    context.lineBeginContext = ContextSwitcher(lineBeginContextText, context.syntax.contexts)
    
    if _parseBoolAttribute(xmlElement.attrib.get('fallthrough', 'false')):
        fallthroughContextText = _safeGetRequiredAttribute(xmlElement, 'fallthroughContext', '#stay')
        context.fallthroughContext = ContextSwitcher(fallthroughContextText, context.syntax.contexts)
    else:
        context.fallthroughContext = None
    
    context.dynamic = xmlElement.attrib.get('dynamic', False)
    
    # load rules
    context.rules = _loadChildRules(context, xmlElement)

################################################################################
##                               Syntax
################################################################################

def _loadAttributeToFormatMap(highlightingElement):
    defaultTheme = ColorTheme()
    attributeToFormatMap = {}
    
    itemDatasElement = highlightingElement.find('itemDatas')
    for item in itemDatasElement.findall('itemData'):
        attribute, defaultStyleName = item.get('name'), item.get('defStyleNum')
        
        if not defaultStyleName in defaultTheme.format:
            print >> sys.stderr, "Unknown default style '%s'" % defaultStyleName
            defaultStyleName = 'dsNormal'
            
        format = copy.copy(defaultTheme.format[defaultStyleName])

        if 'color' in item.attrib:
            format.color = item.attrib['color']
        if 'selColor' in item.attrib:
            format.selectionColor = item.attrib['selColor']
        if 'italic' in item.attrib:
            format.italic = _parseBoolAttribute(item.attrib['italic'])
        if 'bold' in item.attrib:
            format.bold = _parseBoolAttribute(item.attrib['bold'])
        if 'underline' in item.attrib:
            format.underline = _parseBoolAttribute(item.attrib['underline'])
        if 'strikeout' in item.attrib:
            format.strikeout = _parseBoolAttribute(item.attrib['strikeout'])
        if 'spellChecking' in item.attrib:
            format.spellChecking = _parseBoolAttribute(item.attrib['spellChecking'])
        
        attribute = attribute.lower()  # style names are not case sensetive
        attributeToFormatMap[attribute] = format
    
    return attributeToFormatMap
    
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
    syntax.attributeToFormatMap = _loadAttributeToFormatMap(highlightingElement)
    
    # parse contexts
    _loadContexts(highlightingElement, syntax)

    generalElement = root.find('general')
    keywordsElement = root.find('keywords')
    
    # TODO not supported
    #syntax.keywordsCaseSensetive = _parseBoolAttribute(keywordsElement.get('casesensitive', "true"))
    
    return syntax
