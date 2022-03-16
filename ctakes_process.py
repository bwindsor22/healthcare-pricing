import os
from pathlib import Path
import subprocess
from pricelist_loader import data_formatted
from secret import UMLS_API_KEY

base = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/output/')
ctakes_in_folder = base / 'input_files'
ctakes_out_folder = base / 'output_files'
ctakes_pipeline = '/Users/bradwindsor/classwork/nlphealthcare/final-proj/apache-ctakes-4.0.0.1/bin/runClinicalPipeline.sh'

def remove_all_files(dir):
    dir = str(dir)
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

def make_all_dirs(dirs):
    for dir in dirs:
        dir.mkdir(exist_ok=True)

def run_ctakes_process():
    all_data = data_formatted()
    failures = []
    for dataset, dat in all_data.items():
        # dataset = 'nyu'
        # dat = data[dataset]

        in_ = ctakes_in_folder / dataset
        out_ = ctakes_out_folder / dataset
        make_all_dirs([in_, out_])

        remove_all_files(in_)
        remove_all_files(out_)

        for i, row in dat.iterrows():
            outfile = in_ / f'{i}.txt'
            with open(str(outfile), 'w') as f:
                f.write(str(row['description']))

        args = ["bash", ctakes_pipeline, "--key", UMLS_API_KEY, "-i", str(in_), "--xmiOut", str(out_)]
        try:
            print(subprocess.check_output(args))
        except Exception:
            failures.append(dataset)
        print('finished', dataset)
    print('failures', failures)
"""
finished jhmc
failures ['nyp']
"""

if __name__ == '__main__':
    run_ctakes_process()