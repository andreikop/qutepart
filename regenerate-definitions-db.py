#!/usr/bin/env python

import os.path
import json

from qutepart.Syntax import Syntax

def main():
    xmlFilesPath = os.path.join(os.path.dirname(__file__), 'qutepart', 'syntax')
    xmlFileNames = [fileName for fileName in os.listdir(xmlFilesPath) \
                        if fileName.endswith('.xml')]
    
    nameToDefinition = {}
    mimeTypeToDefinition = {}
    extensionToDefinition = {}

    for xmlFileName in xmlFileNames:
        xmlFilePath = os.path.join(xmlFilesPath, xmlFileName)
        syntax = Syntax(xmlFilePath)
        if not syntax.name in nameToDefinition or \
           nameToDefinition[syntax.name][0] < syntax.priority:
            nameToDefinition[syntax.name] = (syntax.priority, xmlFileName)
        
        for mimetype in syntax.mimetype:
            if not mimetype in mimeTypeToDefinition or \
               mimeTypeToDefinition[mimetype][0] < syntax.priority:
                mimeTypeToDefinition[mimetype] = (syntax.priority, xmlFileName)
        
        for extension in syntax.extensions:
            if not extension in extensionToDefinition or \
               extensionToDefinition[extension][0] < syntax.priority:
                extensionToDefinition[extension] = (syntax.priority, xmlFileName)
        
    # remove priority, leave only xml file names
    for dictionary in (nameToDefinition, mimeTypeToDefinition, extensionToDefinition):
        newDictionary = {}
        for key, item in dictionary.items():
            newDictionary[key] = item[1]
        dictionary.clear()
        dictionary.update(newDictionary)
    
    result = {}
    result['nameToDefinition'] = nameToDefinition
    result['mimeTypeToDefinition'] = mimeTypeToDefinition
    result['extensionToDefinition'] = extensionToDefinition

    with open(os.path.join(xmlFilesPath, 'syntax_db.json'), 'w') as syntaxDbFile:
        json.dump(result, syntaxDbFile, sort_keys=True, indent=4)
    
    print 'Done. Do not forget to commit the changes'

if __name__ == '__main__':
    main()
