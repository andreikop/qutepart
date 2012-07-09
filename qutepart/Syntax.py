import os.path
import xml.etree.ElementTree

class Syntax:
    """Syntax file parser and container
    """
    def __init__(self, fileName):
        modulePath = os.path.dirname(__file__)
        dataFilePath = os.path.join(modulePath, "syntax", fileName)
        with open(dataFilePath, 'r') as dataFile:
            root = xml.etree.ElementTree.parse(dataFile).getroot()
        
        # read attributes
        for key, value in root.items():
            setattr(self, key, value)
        
        hlgElement = root.find('highlighting')
        
        # parse lists
        self._lists = {}  # list name: list
        for listElement in hlgElement.findall('list'):
            items = [item.text \
                        for item in listElement.findall('item')]
            self._lists[listElement.attrib['name']] = items

        print self._lists
