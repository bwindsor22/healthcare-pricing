import json
import pandas as pd
import spacy
from pathlib import Path
from nltk.stem.snowball import SnowballStemmer
resources = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/resources/')

"""
Total Number of All U.S. Hospitals	6,090
"""
generic_cols = ['description', 'additional_desc', 'cash_charge', 'united_charge']


def load_nyp():
    """
    https://www.nyp.org/patients-visitors/paying-for-care/hospital-price-transparency/standard-charges
    """
    items_path = resources / 'NYP-data-1.json'
    diseases_path = resources / 'NYP-data-2.json'
    items_costs = json.loads(items_path.read_text())
    diseases_costs = json.loads(diseases_path.read_text())
    return items_costs, diseases_costs

def load_sinai():
    """
    https://www.mountsinai.org/about/insurance/msh/price-transparency
    """
    path = resources / 'mount-sinai.csv'
    data = pd.read_csv(str(path))
    return data

def load_nyu():
    """
    https://med.nyu.edu/standard-charges/nyu-langone-health-standard-charges
    """
    path = resources / 'nyu-langone.csv'
    data = pd.read_csv(str(path), encoding='iso-8859-1')
    return data


def load_siuh():
    """
    https://www.northshoremc.org/price-transparency
    staten island university hospital
    """
    path = resources / 'SIUH.csv'
    data = pd.read_csv(str(path))
    return data

def load_lenox():
    """
    https://www.northshoremc.org/price-transparency
    staten island university hospital
    """
    path = resources / 'LENOX_HILL.csv'
    data = pd.read_csv(str(path))
    return data

def load_jhmc():
    """
    https://jamaicahospital.org/paying-for-care/price-transparency/
    """
    path = resources / 'JH_pysician_proc.csv'
    data1 = pd.read_csv(str(path))
    path = resources / 'JHCDM_treatments_items.csv'
    data2 = pd.read_csv(str(path))
    data2.columns = data2.iloc[0]
    data2 = data2[1:]
    data2.insert(2, 'other', '')
    return data1, data2

def data_formatted():
    nyp_items, nyp_diseases = load_nyp() # also by provider
    sinai = load_sinai() # by provider. need to dedupe
    nyu = load_nyu() # description, category of service. single price
    siuh = load_siuh() # description, category of service. single price
    lenox = load_lenox() # description, category of service. single price
    jhmc_proc, jhmc_items = load_jhmc()

    ###
    # reformat all

    #SIUH
    size = siuh.__len__()
    siuh = siuh[['Charge Description', 'Current\rPrice']]
    siuh.insert(1, 'a', ['' for _ in range(size)])
    siuh.insert(3, 'b', [0 for _ in range(size)])
    siuh.columns = generic_cols

    #LENNOX HILL
    size = lenox.__len__()
    lenox = lenox[['Charge Description', 'Current\rPrice']]
    lenox.insert(1, 'a', ['' for _ in range(size)])
    lenox.insert(3, 'b', [0 for _ in range(size)])
    lenox.columns = generic_cols

    ## NYP
    nyp_df = pd.DataFrame(nyp_items)
    temp_df = pd.DataFrame(nyp_diseases)

    nyp_df = nyp_df[['Description', 'Inpatient/Outpatient', 'Gross Charges', 'United']]
    temp_df1 = temp_df[['EAPG Desc', 'EAPG']]
    temp_df1['N/A'] = 0
    temp_df1['united'] = temp_df['United Commuity Plan Essential Plan Medical Service Price']

    nyp_df.columns = generic_cols
    temp_df1.columns = generic_cols
    nyp_df = pd.concat([nyp_df, temp_df1], axis=0)


    ## SINIA
    temp = sinai[sinai['Payer/Plan Name'] == 'UNITEDHEALTHCARE OF NEW YORK INC NY DUAL COMPLETE']
    sinai_df = temp[['DRG/CPT/HCPCS Description', 'DRG/CPT/HCPCS Code']]
    sinai_df['N/A'] = 0
    sinai_df['Negotiated Charge'] = temp['Negotiated Charge']
    sinai_df.columns = generic_cols


    # NYU
    nyu_df = nyu[['DESCRIPTION', 'CATEGORY OF SERVICE', 'CHARGE AMOUNT']]
    nyu_df['tmp'] = 0
    nyu_df.columns = generic_cols
    def to_num(x):
        if x == 'Not separately payable':
            return 0
        elif isinstance(x, str):
            return float(x[1:].replace(',', ''))
        elif x == float('nan'):
            return 0
        elif isinstance(x, float) or isinstance(x, int):
            return x
        else:
            print('not found')
    nyu_df['cash_charge'] = nyu_df['cash_charge'].apply(to_num)

    #jhmc
    jhmc_proc.insert(1, 'blank', '')
    jhmc_proc.columns = generic_cols
    jhmc_items.insert(1, 'blank', '')
    jhmc_items.columns = generic_cols
    jhmc = pd.concat([jhmc_proc, jhmc_items], axis=0)

    dataset = {
        'nyu': nyu_df,
        'sinai': sinai_df,
        'nyp': nyp_df,
        'lenox': lenox,
        'siuh': siuh,
        'jhmc': jhmc,
    }



    for name, data in dataset.items():
        data['cash_charge'] = pd.to_numeric(data['cash_charge'], errors='coerce')
        data['united_charge'] = pd.to_numeric(data['united_charge'], errors='coerce')
        dataset[name] = data

    for name, data in dataset.items():
        dataset[name] = data.fillna(0)

    # retitle_columns
    for name, data in dataset.items():
        data.rename({
            'additional_desc': name + '_additional_desc',
            'cash_charge': name + '_cash_charge',
            'united_charge': name + '_united_charge'
        })


    return dataset

if __name__ == '__main__':
    data_formatted()