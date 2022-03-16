import os
from pathlib import Path
import subprocess
from pricelist_loader import data_formatted
from secret import UMLS_API_KEY

base = Path('/Users/bradwindsor/classwork/nlphealthcare/final-proj/output/')
ctakes_in_folder = base / 'grid_out'
ctakes_out_folder = base / 'output_files'
ctakes_pipeline = '/Users/bradwindsor/classwork/nlphealthcare/final-proj/apache-ctakes-4.0.0.1/bin/runClinicalPipeline.sh'


def run_ctakes_process():
    for in_ in ctakes_in_folder.glob('*'):
        args = ["bash", ctakes_pipeline, "--key", UMLS_API_KEY, "-i", str(in_), "--xmiOut", str(ctakes_out_folder)]
        try:
            print(subprocess.check_output(args))
        except Exception:
            pass

"""
finished jhmc
failures ['nyp']
"""

if __name__ == '__main__':
    run_ctakes_process()