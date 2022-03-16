from pricelist_loader import data_formatted, generic_cols
from ctakes_process import ctakes_out_folder, ctakes_in_folder
import xml.etree.ElementTree as ET
import pandas as pd
import seaborn
import seaborn as sns
sns.set_theme(style="whitegrid")
import statistics
import numpy as np
from copy import deepcopy
import pickle
def digits(txt):
    return  [int(s) for s in txt.split() if s.isdigit()]



def medicine_compare(all_data, limit_more_than=1, meds_method="RXNORM"):
    meds_select = dict()
    for dataset, dat in all_data.items():
        ctakes_output = ctakes_out_folder / dataset
        text_input = ctakes_in_folder / dataset

        ctakes_files = ctakes_output.glob('*')

        rows_meds = []
        excs = 0
        for file in ctakes_files:
            try:
                file_stem = file.stem.replace('.xmi', '')
                source_text_file = text_input / file_stem
                source_text = source_text_file.read_text()
                tree = ET.parse(str(file))
                root = tree.getroot()
                eles = [c for c in root]
                if meds_method=="RXNORM":
                    meds = [e for e in eles if 'codingScheme' in e.attrib and e.attrib['codingScheme'] == 'RXNORM']
                    if len(meds):
                        if len(meds) == 0:
                            med = meds[0]
                            med_code = med.attrib['code']
                            med_text = med.attrib['preferredText']
                        else:
                            codes = set()
                            texts = set()
                            for med in meds:
                                codes.add(med.attrib['code'])
                                texts.add(med.attrib['preferredText'])
                            med_code = '-'.join(sorted(list(codes)))
                            med_text = '-'.join(sorted(list(texts)))
                        row_num = file.stem.replace('.txt', '')
                        row = dat.iloc[int(row_num)]

                        new_row = [med_code, med_text, *row.tolist()]
                        rows_meds.append(new_row)
                elif meds_method == "MEDICATION_MENION":
                    meds = [e for e in eles if e.tag == '{http:///org/apache/ctakes/typesystem/type/textsem.ecore}MedicationMention']
                    if len(meds):
                        if len(meds) == 0:
                            med = meds[0]
                            med_code = source_text[int(med.attrib['begin']):int(med.attrib['end'])].upper()
                            med_text = source_text[int(med.attrib['begin']):int(med.attrib['end'])]
                        else:
                            codes = set()
                            texts = set()
                            for med in meds:
                                # codes.add(med.attrib['ontologyConceptArr'])
                                codes.add(source_text[int(med.attrib['begin']):int(med.attrib['end'])])
                                texts.add(source_text[int(med.attrib['begin']):int(med.attrib['end'])])
                            med_code = '-'.join(sorted(list(codes)))
                            med_text = '-'.join(sorted(list(texts)))
                        row_num = file.stem.replace('.txt', '')
                        row = dat.iloc[int(row_num)]

                        new_row = [med_code, med_text, *row.tolist()]
                        rows_meds.append(new_row)
                elif meds_method == "PROCEDURE_MENTION":
                    meds = [e for e in eles if e.tag == '{http:///org/apache/ctakes/typesystem/type/textsem.ecore}ProcedureMention']
                    if len(meds):
                        if len(meds) == 0:
                            med = meds[0]
                            med_code = source_text[int(med.attrib['begin']):int(med.attrib['end'])].upper()
                            med_text = source_text[int(med.attrib['begin']):int(med.attrib['end'])]
                        else:
                            codes = set()
                            texts = set()
                            for med in meds:
                                codes.add(source_text[int(med.attrib['begin']):int(med.attrib['end'])])
                                texts.add(source_text[int(med.attrib['begin']):int(med.attrib['end'])])
                            med_code = '-'.join(sorted(list(codes)))
                            med_text = '-'.join(sorted(list(texts)))
                        row_num = file.stem.replace('.txt', '')
                        row = dat.iloc[int(row_num)]

                        new_row = [med_code, med_text, *row.tolist()]
                        rows_meds.append(new_row)

            except Exception:
                print('Exception # ', excs, 'on dataset', dataset)
                excs += 1
                pass

        df = pd.DataFrame(rows_meds, columns=['Code', 'code desc', *generic_cols])

        # remove frequent counts
        counts = df[['Code', 'code desc']].groupby(['Code']).count()
        ignore = counts[counts['code desc'] > limit_more_than]
        ignore.reset_index(inplace=True)
        ignore = ignore.rename(columns={'index': 'Code'})

        # semijoinminus
        df_rare_found = pd.merge(df, ignore, on=['Code'], how="outer", indicator=True
                      ).query('_merge=="left_only"')

        meds_select[dataset] = df_rare_found

    return meds_select

def merge_and_compare(meds_select, compare_col='cash_charge'):
    # for name, df in meds_select.items():
    #     meds_select[name] = df[['Code', compare_col]]

    div_series = dict()
    merge_tallies = []
    passed = set()
    for name1, df1 in meds_select.items():
        for name2, df2 in meds_select.items():
            if name1 is not name2 and name2 not in passed:
                df1 = df1[df1[compare_col] != 0]
                df2 = df2[df2[compare_col] != 0]
                merged = pd.merge(df1, df2, on=['Code'], how='inner')
                merge_tallies.append([name1, name2, len(merged.index)])

                if len(merged.index) >= 5:
                    key = f'{name1} / {name2}'
                    div = merged.apply(lambda row: row[f'{compare_col}_x'] / row[f'{compare_col}_y'], axis=1)
                    if div.mean() < 1:
                        key = f'{name2} / {name1}'
                        div = merged.apply(lambda row:  row[f'{compare_col}_y'] / row[f'{compare_col}_x'], axis=1)
                    div_series[key] = [x for x in div.tolist() if x <= 10]
        passed.add(name1)
    tallies = pd.DataFrame(merge_tallies, columns=['dataset 1', 'dataset 2', 'count'])
    return tallies, div_series

# from functools import reduce
# df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['Code'],
#                                             how='outer'), dfs)
# df_merged.to_csv('./out.csv')


if __name__ == '__main__':
    all_data = data_formatted()
    limit_more_than = 20

    dat = medicine_compare(deepcopy(all_data), limit_more_than=limit_more_than)
    tallies, numbers = merge_and_compare(deepcopy(dat))
    tallies_u, numbers_u = merge_and_compare(deepcopy(dat), compare_col='united_charge')
    pickle.dump([tallies, numbers, tallies_u, numbers_u], open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/rxnorm.pkl', 'wb'))

    dat = medicine_compare(deepcopy(all_data), limit_more_than=limit_more_than, meds_method="PROCEDURE_MENTION")
    tallies, numbers = merge_and_compare(deepcopy(dat))
    tallies_u, numbers_u = merge_and_compare(deepcopy(dat), compare_col='united_charge')
    pickle.dump([tallies, numbers, tallies_u, numbers_u], open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/procedure.pkl', 'wb'))



    dat = medicine_compare(deepcopy(all_data), limit_more_than=limit_more_than, meds_method="MEDICATION_MENION")
    tallies, numbers = merge_and_compare(deepcopy(dat))
    tallies_u, numbers_u = merge_and_compare(deepcopy(dat), compare_col='united_charge')
    pickle.dump([tallies, numbers, tallies_u, numbers_u], open('/Users/bradwindsor/classwork/nlphealthcare/final-proj/finished_datasets/medication.pkl', 'wb'))





    print('hi')
