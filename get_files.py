"""
File: get_files.py
Author: Chuncheng Zhang
Date: 2025-04-16
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2025-04-16 ------------------------
# Requirements and constants
import joblib
import pandas as pd
from loguru import logger
from tqdm.auto import tqdm
from util.file_trip import get_scruaf_folders, get_scruaf_nii_files


# %% ---- 2025-04-16 ------------------------
# Function and class
def this_get_scruaf_folders():
    '''
    Get scruaf folders from caching or searching.
    '''

    filename = './cache/scruaf_folders.bin'
    try:
        folders = joblib.load(filename)
        logger.info(f'Using cached scruaf folders from {filename}.')
    except:
        logger.debug('Searching scruaf folders.')
        folders = get_scruaf_folders()
        joblib.dump(folders, filename)
        logger.info(f'Saved scruaf folders: {filename}.')
    finally:
        return folders

def this_get_table(folders:list):
    '''
    Get file table from caching or searching.
    '''
    filename = './cache/table.pkl'
    try:
        table = pd.read_pickle(filename)
        logger.info(f'Using cached table: {filename}.')
    except:
        logger.debug('Searching scruaf nii files.')
        # Sequentially process folders to get scruaf nii files.
        table = []

        for folder in tqdm(folders, 'Find files'):
            subject = folder.parent.parent.name
            session = folder.parent.name
            files = get_scruaf_nii_files(folder)
            table.extend([(subject, session, e.parent.name, e.name, e) for e in files])

        # Convert table into DataFrame
        table = pd.DataFrame(table, columns=['subject', 'session', 'run', 'name', 'full'])
        table.to_pickle('./cache/table.pkl')
        logger.info(f'Saved table: {filename}.')
    finally:
        return table

# %% ---- 2025-04-16 ------------------------
# Play ground
folders = this_get_scruaf_folders()
table = this_get_table(folders)
print(table)

# %% ---- 2025-04-16 ------------------------
# Pending



# %% ---- 2025-04-16 ------------------------
# Pending
