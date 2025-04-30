"""
File: file_trip.py
Author: Chuncheng Zhang
Date: 2025-04-15
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Find and use files.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-04-15 ------------------------
# Requirements and constants
import os
import sys
import subprocess
from pathlib import Path



# %% ---- 2025-04-15 ------------------------
# Function and class

def get_scruaf_folders():
    '''
    Get folders named as SCRUAF.
    '''
    root = Path('/nfs/nica-history-216/180/Context_learning/Context_learning_2024_clean_data')
    output = subprocess.check_output(['find', root, '-type', 'd', '-name', 'FunImgSCRUAF'])
    found = [Path(e.decode()) for e in output.split(b'\n') if e]
    return found

def get_ds_folders():
    '''
    Get folders named as *.ds
    '''
    root = Path('/nfs/nica-history-216/180/Context_learning/Context_learning_2024_raw_data')
    output = subprocess.check_output(['find', root, '-type', 'd', '-name', '*_G25IA_*.ds'])
    found = [Path(e.decode()) for e in output.split(b'\n') if e]
    return found

def get_ds_mrk_files(folder:Path):
    '''
    Get *.mat named files inside folder.

    :param folder Path: The given folder.
    :return list: The list of found files.
    '''
    files = list(folder.rglob('MarkerFile.mrk'))
    return files

def get_scruaf_nii_files(folder:Path):
    '''
    Get scruaf*.nii named files inside folder.

    :param folder Path: The given folder.
    :return list: The list of found files.
    '''
    files = list(folder.rglob('scruaf*.nii'))
    return files


# %% ---- 2025-04-15 ------------------------
# Play ground
if __name__ == '__main__':
    folders = get_scruaf_folders()
    print(folders[0])

    files = get_scruaf_nii_files(folders[0])
    print(files)


# %% ---- 2025-04-15 ------------------------
# Pending



# %% ---- 2025-04-15 ------------------------
# Pending

# %%
