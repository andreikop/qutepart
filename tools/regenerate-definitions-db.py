#!/usr/bin/env python

import os.path
import json

import sys
sys.path.append('.')
sys.path.append('..')
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))


from qutepart.syntax.loader import loadSyntax
from qutepart.syntax import SyntaxManager, Syntax


def main():
    syntaxDataPath = os.path.join(os.path.dirname(__file__), '..', 'qutepart', 'syntax', 'data')
    xmlFilesPath = os.path.join(syntaxDataPath, 'xml')
    xmlFileNames = [fileName for fileName in os.listdir(xmlFilesPath) \
                        if fileName.endswith('.xml')]

    syntaxNameToXmlFileName = {}
    mimeTypeToXmlFileName = {}
    extensionToXmlFileName = {}
    firstLineToXmlFileName = {}

    for xmlFileName in xmlFileNames:
        xmlFilePath = os.path.join(xmlFilesPath, xmlFileName)
        syntax = Syntax(None)
        loadSyntax(syntax, xmlFilePath)
        if not syntax.name in syntaxNameToXmlFileName or \
           syntaxNameToXmlFileName[syntax.name][0] < syntax.priority:
            syntaxNameToXmlFileName[syntax.name] = (syntax.priority, xmlFileName)

        if syntax.mimetype:
            for mimetype in syntax.mimetype:
                if not mimetype in mimeTypeToXmlFileName or \
                   mimeTypeToXmlFileName[mimetype][0] < syntax.priority:
                    mimeTypeToXmlFileName[mimetype] = (syntax.priority, xmlFileName)

        if syntax.extensions:
            for extension in syntax.extensions:
                if extension not in extensionToXmlFileName or \
                   extensionToXmlFileName[extension][0] < syntax.priority:
                    extensionToXmlFileName[extension] = (syntax.priority, xmlFileName)
                elif extension in extensionToXmlFileName:

        if syntax.firstLineGlobs:
            for glob in syntax.firstLineGlobs:
                if not glob in firstLineToXmlFileName or \
                   firstLineToXmlFileName[glob][0] < syntax.priority:
                    firstLineToXmlFileName[glob] = (syntax.priority, xmlFileName)

    # remove priority, leave only xml file names
    for dictionary in (syntaxNameToXmlFileName,
                       mimeTypeToXmlFileName,
                       extensionToXmlFileName,
                       firstLineToXmlFileName):
        newDictionary = {}
        for key, item in dictionary.items():
            newDictionary[key] = item[1]
        dictionary.clear()
        dictionary.update(newDictionary)

    result = {}
    result['syntaxNameToXmlFileName'] = syntaxNameToXmlFileName
    result['mimeTypeToXmlFileName'] = mimeTypeToXmlFileName
    result['extensionToXmlFileName'] = extensionToXmlFileName
    result['firstLineToXmlFileName'] = firstLineToXmlFileName

    with open(os.path.join(syntaxDataPath, 'syntax_db.json'), 'w') as syntaxDbFile:
        json.dump(result, syntaxDbFile, sort_keys=True, indent=4)

    print 'Done. Do not forget to commit the changes'

if __name__ == '__main__':
    main()
