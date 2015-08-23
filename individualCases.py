import os, sys
import config
import run
__author__ = 'wang'

def check_arguments():
    if len(sys.argv) != 2:
        print
        sys.exit(['Usage: ' + sys.argv[0] + ' <textfile>'])

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
    for fMriFolder in config.fMRI_Locations:
        for folder in folders:
            i = os.walk(folder).next()
            if not i[1]: # If no subfolder, continue, else fail. Make sure that it is at the deepest level
                dataFromFile = i[2][0].split("_")    #['ADNI', '130', 'S', '2391', 'MR', 'Resting', 'State', 'fMRI', 'br', 'raw', '20110622150204096', '1', 'S112049', 'I240902.dcm']
                if len(dataFromFile) is 14: # Make sure it's the proper DCM file
                    dataFromFile.append(i[0]) # i - ['<path>','<folders in the path>','<files in the path>']
                    dataList.append(dataFromFile)
    result = pool.map(run.do_work, dataList)
    print result