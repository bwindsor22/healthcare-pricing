import xml.etree.ElementTree as ET
input = '/Users/bradwindsor/classwork/nlphealthcare/final-proj/apache-ctakes-4.0.0.1/desc/notes.txt.xmi'

tree = ET.parse(input)
root = tree.getroot()
for child in root:
    print(child.tag, child.attrib)
eles = [c for c in root]
print('hi')


"""
Abdominal CT
{'{http://www.omg.org/XMI}id': '203', 'sofa': '1', 'begin': '0', 'end': '12', 'chunkType': 'NP'}

osteoperosis
{'{http://www.omg.org/XMI}id': '266', 'sofa': '1', 'begin': '71', 'end': '83', 'id': '0', 'ontologyConceptArr': '253', 'typeID': '2', 'discoveryTechnique': '1', 'confidence': '0.0', 'polarity': '1', 'uncertainty': '0', 'conditional': 'false', 'generic': 'false', 'subject': 'patient', 'historyOf': '0'}


Ctakes:
- A parser with some combination of:
    - noun phrase (from "Chunk")
    - DiseaseDisorderMention
    - SignSymptomMention
    - AnatomicalSiteMention
    - ProcedureMention
    
- also use: 
    -UMLS concept with snowmed ct codes
        https://snomedbrowser.com/Codes/Details/64859006

.attrib['codingScheme'] == 'RXNORM'
A = [e for e in eles if 'codingScheme' in e.attrib and e.attrib['codingScheme'] == 'RXNORM']

osteoperosis here: 
/Users/bradwindsor/classwork/nlphealthcare/final-proj/resources/SnomedCT_USEditionRF2_PRODUCTION_20210901T120000Z/Snapshot/Terminology/sct2_Description_Snapshot-en_US1000124_20210901.txt
"""