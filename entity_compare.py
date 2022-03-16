import spacy
from pathlib import Path
import unittest

resources = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/resources/')

class TestExtract(unittest.TestCase):

    def setUp(self):
        nlp = spacy.load("en_core_sci_scibert")
        self.nlp = nlp

    def test_given_string(self):
        text = 'Alterations in the hypocretin receptor 2 and preprohypocretin genes produce narcolepsy in some animals.'
        doc = self.nlp(text)
        print(doc.ents)

    def test_mimic_samp(self):
        source = resources / 'test' / 'notes.txt'
        text = ' '.join(source.read_text().split())
        doc = self.nlp(text)
        print(doc.ents)
