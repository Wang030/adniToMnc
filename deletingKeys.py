import os, sys
import config
import run
from databaseManager import databaseManager
__author__ = 'wang'

def check_arguments():
    if len(sys.argv) != 2:
        print
        sys.exit('Usage: ' + sys.argv[0] + ' <textfile>')

def read_from_file(listOfFolders):
    with open(listOfFolders,'r') as f:
        lines = f.readlines()
    data = [x.strip() for x in lines]
    return data

if __name__ == '__main__':

    check_arguments()
    pool = run.initiate_pool()

    dataList = []
    folders = read_from_file(sys.argv[1])
    dbm = databaseManager(config.libraryFile)
    [dbm.delete_keys(folder) for folder in folders] # Delete Keys
    dbm.close()