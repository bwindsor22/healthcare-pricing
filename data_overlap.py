import json
import pandas as pd
import spacy
from pathlib import Path
from ctakes_parser import ctakes_parser
from nltk.stem.snowball import SnowballStemmer

from img_loader import load_imgs_as_dfs
from pricelist_loader import data_formatted

resources = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/resources/')

# nlp = spacy.load("en_core_sci_scibert")
nlp = spacy.load("en_core_sci_sm")
stemmer = SnowballStemmer("english")


def vanilla_merge(dataset, key1, key2):
    df1 = dataset[key1].merge(dataset[key2], how='inner', on='description', suffixes=(key1, key2))
    print(key1, key2, ' merge to find rows :', df1.size)
    return df1


def apply_spacy(text):
    if isinstance(text, float):
        return set()
    text = ' '.join(str(text).split())
    doc = nlp(text)
    lemmas = set([stemmer.stem(e.lemma_.lower()) for e in doc.ents])
    return lemmas



def join_spacy(df1, df2, key1, key2):
    max_2 = []
    for i, row1 in df1.iterrows():
        max_j = -1
        max_overlap = 0
        for j, row2 in df2.iterrows():
            overlap = len(row1['toks'].intersection(row2['toks']))
            if overlap > max_overlap and overlap > 2:
                max_j = j
                max_overlap = overlap
        max_2.append(max_j)
    df1['join_keys'] = max_2
    result = df1.merge(df2, how='inner', left_on='join_keys', right_index=True, suffixes=(key1, key2))
    print('joined ', key1, key2, ' size ', result.size)
    return result

def run_compare():
    dataset = data_formatted()

    ### vanilla join
    # df1 = dataset['nyu'].merge(dataset['sinai'], how='inner', on='description')
    # df2 = dataset['sinai'].merge(dataset['nyp'], how='inner', on='description')
    # df3 = dataset['nyu'].merge(dataset['nyp'], how='inner', on='description')
    #
    df1 = vanilla_merge(dataset, 'nyu', 'jhmc')
    df2 = vanilla_merge(dataset, 'nyu', 'siuh')
    df3 = vanilla_merge(dataset, 'sinai', 'siuh')

    ### spacy join
    nyu = dataset['nyu']
    nyu['toks'] = nyu['description'].apply(apply_spacy)
    print('finished first set')
    jhmc = dataset['jhmc']
    jhmc['toks'] = jhmc['description'].apply(apply_spacy)
    print('finished SECOND set')
    siuh = dataset['siuh']
    siuh['toks'] = siuh['description'].apply(apply_spacy)
    print('finished third set')
    sinai = dataset['sinai']
    sinai['toks'] = sinai['description'].apply(apply_spacy)
    print('finished fourth set')


    df3 = join_spacy(nyu, siuh, 'nyu', 'siuh')
    print('spacy nyu, siuh size', df3.size)

    df3 = join_spacy(sinai, siuh, 'sinai', 'siuh')
    print('spacy sinai, siuh size', df3.size)

    df3 = join_spacy(nyu, jhmc, 'nyu', 'jhmc')
    print('spacy nyu-jhmc size', df3.size)





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_join_img()