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
import mne
import joblib
import pandas as pd
from loguru import logger
from tqdm.auto import tqdm
from util.file_trip import get_scruaf_folders, get_scruaf_nii_files
from util.file_trip import get_ds_folders, get_ds_mrk_files
from util.file_trip import get_cnt_files


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

def this_get_ds_folders():
    filename = './cache/ds_folders.bin'
    try:
        folders=joblib.load(filename)
        logger.info(f'Using cached ds folders from {filename}.')
    except:
        logger.debug('Searching ds folders.')
        folders = get_ds_folders()
        joblib.dump(folders, filename)
        logger.info(f'Saved ds folders: {filename}')
    finally:
        return folders

def this_get_cnt_files():
    filename = './cache/cnt_files.bin'
    try:
        files = joblib.load(filename)
        logger.info(f'Using cached cnt files from {filename}.')
    except:
        logger.debug('Searching ds folders.')
        files = get_cnt_files()
        joblib.dump(files, filename)
        logger.info(f'Saved cnt files: {filename}')
    finally:
        return files

def this_get_table_eeg(files:list):
    '''
    Get file table from caching or searching.
    '''
    filename = './cache/table-eeg.pkl'
    try:
        table = pd.read_pickle(filename)
        logger.info(f'Using cached table: {filename}')
    except:
        logger.debug('Searching cnt files.')
        table = []
        for file in tqdm(files, 'Appending tables'):
            subject = file.parent.parent.name
            session = 'AAD'
            run = 'run1'
            name = file.name
            full = file
            table.append((subject, session, run, name, full))
        # Convert table into DataFrame
        table = pd.DataFrame(table, columns=['subject', 'session', 'run', 'name', 'full'])

        def count_length(p):
            raw = mne.io.read_raw(p)
            length = raw.duration
            return length

        table['length'] = table['full'].map(count_length)

        table.to_pickle(filename)
        logger.info(f'Saved table: {filename}.')
    finally:
        return table

def this_get_table_fmri(folders:list):
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
        table.to_pickle(filename)
        logger.info(f'Saved table: {filename}.')
    finally:
        return table

def this_get_table_meg(folders:list):
    filename = './cache/table-meg.pkl'
    try:
        table = pd.read_pickle(filename)
        logger.info(f'Using cached table: {filename}.')
    except:
        logger.debug('Searching MarkerFile files.')
        # Sequentially process folders to get scruaf nii files.
        table = []

        for folder in tqdm(folders, 'Find files'):
            subject = folder.parent.parent.name
            session = folder.parent.name
            files = get_ds_mrk_files(folder)
            table.extend([(subject, session, e.parent.name, e.name, e) for e in files])

        # Convert table into DataFrame
        table = pd.DataFrame(table, columns=['subject', 'session', 'run', 'name', 'full'])

        def count_length(p):
            raw = mne.io.read_raw(p.parent)
            length = raw.duration
            return length

        table['length'] = table['full'].map(count_length)
        
        table.to_pickle(filename)
        logger.info(f'Saved table: {filename}.')
    finally:
        return table

# %% ---- 2025-04-16 ------------------------
# Play ground
folders_fmri = this_get_scruaf_folders()
print(folders_fmri)
table = this_get_table_fmri(folders_fmri)
print(table)

folders_meg = this_get_ds_folders()
print(folders_meg)
table_meg = this_get_table_meg(folders_meg)
print(table_meg)

files_eeg = this_get_cnt_files()
print(files_eeg)
table_eeg = this_get_table_eeg(files_eeg)
print(table_eeg)


# %% ---- 2025-04-16 ------------------------
# Pending
if __name__ == '__main__':
    print(table)
    print(table_meg)
    print(table_eeg)



# %% ---- 2025-04-16 ------------------------
# Pending
