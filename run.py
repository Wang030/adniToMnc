import subprocess
from multiprocessing import Pool
import config
from databaseManager import databaseManager
from ProcessingList import ProcessingList


def do_work(dataFromFile):
    subprocess.call(["python dcmTomnc.py " + '#'.join(dataFromFile)], shell=True)
    return "Done. Please find output in - " + config.output_folder


def initiate_pool():
    if config.numberOfProcesses is 0:
        pool = Pool()
    else:
        pool = Pool(processes=config.numberOfProcesses)
    return pool

if __name__ == '__main__':
    pool = initiate_pool()
    foldersList = ProcessingList()
    newFolder = "/data/data02/ADNI/new_raw/MCI/002_S_4521/MRI/rsfmri/Extended_Resting_State_fMRI/2014-03-14_06_27_32.0/S214881/"
    foldersList.add(newFolder)
    result = pool.map(do_work, foldersList.data())
    #dbm = databaseManager(config.libraryFile)
    #for fMriFolder in config.fMRI_Locations:
    #    for newFolder in dbm.check_new_files(fMriFolder):
    #        foldersList.add(newFolder)
    #result = pool.map(do_work, foldersList)
    #dbm.close()
    print result