"""This module manages knows file => parser class associations and 
holds already created Syntax instances
Use this module for getting Syntax'es
"""

_nameToDefinitionName = {}  # name: (priproty, definition name)
_mimeTypeToDefinitionName = {}  # mime type: (priproty, definition name)
_extensionToDefinitionName = {}  # extension: (priproty, definition name)

_definitionNameToSyntaxInstance = {}  # already created Syntax instances

def _allDefinitions():
    xmlFilesPath = os.path.join(os.path.dirname(__file__), 'syntax')
    return [os.path.join(xmlFilesPath, xmlFileName) \
                for xmlFileName in os.listdir(xmlFilesPath) \
                    if xmlFileName.endswith('.xml')]

def _init():
    


def getSyntaxByName(name):
    pass

def getSyntaxBySourceFileName(name):
    pass

def getSyntaxByMimeType(mimeType):
    pass

def getSyntaxByDefinitionName(definitionName):
    pass
