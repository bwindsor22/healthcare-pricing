input = '/Users/bradwindsor/classwork/nlphealthcare/final-proj/apache-ctakes-4.0.0.1/desc/notes-tiny-medicine.txt.xmi'
import xml.etree.ElementTree as ET
tree = ET.parse(input)
root = tree.getroot()
eles = [e for e in root]

print('hi')