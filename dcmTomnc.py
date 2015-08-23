import sys
import subprocess
import os
import shutil
import glob
from datetime import datetime
import databaseManager
import re
import errno

import config

# Executed per scan folder (e.g. /data/data02/ADNI/raw/EMCI/002_S_2043/MRI/rsfmri/2010-12-08_11_31_20.0/S96108)

def removeOtherFilesInFolder(t_folderPath, extToKeep,temp_file_folder):
    otherFiles = []
    for file in os.listdir(t_folderPath):
        if not file.endswith(extToKeep):
            shutil.move(t_folderPath + "/" + file, temp_file_folder)
            otherFiles.append(file)
    return otherFiles


def addBackOtherFiles(folderPath,otherFiles,temp_file_folder):
    for file in otherFiles:
        shutil.move(temp_file_folder + '/' + file, folderPath + "/")


def convert2nii(dcm2nii_command):
    subprocess.call([dcm2nii_command], shell=True)

def checkFolderPath(folderPath):
    if folderPath.endswith("/"):
        folderPath = folderPath[:-1]
    return folderPath

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def create_output_directories(output_folder, subjectID):
    directory = output_folder + "/subject" + subjectID
    make_sure_path_exists(directory + '/anat/')
    make_sure_path_exists(directory + '/fmri/')
    return directory

def convert2mnc(folderPath,MainLogFileLoc,subjectInfo,dateInfo,nii2mnc_path,output_folder):
    logFile = open(MainLogFileLoc, 'a+')
    mriList = []
    k = 0
    for niiFile in glob.glob(folderPath + "/*.nii.gz"):
        k = k + 1
        directory = create_output_directories(output_folder,subjectInfo)
        fMriFile = directory + '/fmri/subject' + subjectInfo + '_' + dateInfo + '_' + str(k) + ".mnc"
        nii2mnc_command = nii2mnc_path + " " + niiFile + " " + fMriFile
        subprocess.call([nii2mnc_command], shell=True)
        rm_command = "rm " + niiFile
        subprocess.call([rm_command], shell=True)
        #############
        info_command = "source /opt/minc-toolkit/minc-toolkit-config.sh; mincinfo " + fMriFile + " | grep \"time\" "
        proc = subprocess.Popen(info_command, stdout=subprocess.PIPE, shell=True)
        timeAxisOnFile = proc.stdout.read().strip()
        if timeAxisOnFile == "":
            if not os.path.exists(output_folder + "/InvalidFMRI/"):
                os.mkdir(output_folder + "/InvalidFMRI/")
            mv_command = "mv " + fMriFile + " " + output_folder + "/InvalidFMRI/"
            subprocess.call([mv_command], shell=True)
            k = k - 1
            logFile.write(fMriFile + " Deleted as FMRI File does not have time axis\n")
        else:
            logFile.write(fMriFile + " Success\n")
        #############
        if k is 1: #Find the MRI scan for these. If k >= 2, its a iteration. DO NOT find MRI for it because we already did.
            mriList.append([subjectInfo, dateInfo])
    logFile.close()
    return mriList

def getDateOnFile(f):
    header_command = "source /opt/minc-toolkit/minc-toolkit-config.sh; mincheader " + f + " | grep \"history\" | sed \"s:.*/\(.*-[0-9]\{2\}\)_[0-9_]*\.0/.*:\\1:\" | sed \"s:-::g\""
    proc = subprocess.Popen(header_command, stdout=subprocess.PIPE, shell=True)
    dateOnFile = proc.stdout.read().strip()
    return dateOnFile


def getCorrespondingMRI(location, subjectID):
    dict = {}
    for f in glob.glob(location + "adni_" + subjectID + "/t1/*.mnc*"):
        dict[getDateOnFile(f)] = f
    return dict
    #return {getDateOnFile(f): f for f in glob.glob(location + "adni_" + subjectID + "/t1/*.mnc*")}


def getMatchingMRI(subjectMRIListWithDates, date):
    format_date = lambda d: d[:4] + "-" + d[4:6] + "-" + d[6:8]
    get_datetime = lambda y: datetime.strptime(format_date(y), "%Y-%m-%d")
    date_list = [x for x in subjectMRIListWithDates]
    closest_date = min(date_list, key=lambda d: abs(get_datetime(d) - get_datetime(date)))
    return subjectMRIListWithDates[closest_date]


def searchForMRI(MRIlogFileLoc,output_folder,findMRIList,MRI_Locations):
    MRIlogFile = open(MRIlogFileLoc, 'a+')
    for item in findMRIList:
        subjectID = item[0]
        dateInfo = item[1]
        foundMRI = False
        for location in MRI_Locations:
            if not foundMRI:
                k = 0
                subjectMRIListWithDates = getCorrespondingMRI(location, subjectID)
                if len(subjectMRIListWithDates) is not 0:
                    mriFile = getMatchingMRI(subjectMRIListWithDates, dateInfo)
                    k = k + 1
                    fileName, extension = os.path.splitext(mriFile)

                    directory = create_output_directories(output_folder,subjectID)
                    mriLink = directory + '/anat/subject' + subjectID + '_' + dateInfo + '_' + str(k)
                    if extension == '.mnc':
                        mriLink = mriLink +  ".mnc"
                    elif extension == '.gz':
                        mriLink = mriLink + ".mnc.gz"
                    if not os.path.isfile(mriLink):
                        os.symlink(mriFile, mriLink)
                    foundMRI = True
        if not foundMRI:
            MRIlogFile.write(subjectID + " , " + dateInfo + " 	- MRI NOT FOUND\n")
    MRIlogFile.close()

def checkMRIFiles(l_file,dicomFolder): # For each raw DICOM folder database (e.g. /data/data02/ADNI/raw/)
   folders = databaseManager(l_file)
   list = folders.generateListOfFolders(dicomFolder)
   for folder in list:
       searchForMRI(folder) # Still needs work

def find_scanID(list):
  """Return first item in list where length > 3 and first letter is S"""
  for item in list:
      if re.match("S[0-9]+",item):
          return item

def read_input_info(inputArgv):
    inputArgv = inputArgv.split("#")
    folderPath = inputArgv[-1] # Last in list
    subjectInfo = inputArgv[inputArgv.index("S")+1] # subjectID is the item following S
    dateInfo = [x for x in folderPath.split("/") if re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}", x)][0] #['', 'data', 'data02', 'ADNI', 'raw', 'EMCI', '002_S_4237', 'MRI', 'rsfmri', '2012-11-01_12_29_20.0', 'S174283']
    dateInfo = dateInfo.translate(None, "-_.")[:8] # 2012-11-01_12_29_20.0 --> 20121101
    scanID = find_scanID(inputArgv)
    return folderPath, subjectInfo, dateInfo, scanID

def remove_folder(path):
    files = os.listdir(path)
    if len(files) == 0:
        print "Removing empty folder:", path
        os.rmdir(path)

def read_config_file():
    MRIlogFileLoc = config.MRIlogFileLoc
    MainLogFileLoc = config.logFileLoc

    dcm2nii_path = config.dcm2nii_path
    nii2mnc_path = config.nii2mnc_path
    output_folder = config.output_folder + "/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    temp_file_folder = config.temp_file_folder + "/"
    MRI_Locations = config.MRI_Locations
    return MRIlogFileLoc, MainLogFileLoc, dcm2nii_path, nii2mnc_path, output_folder, temp_file_folder, MRI_Locations

if __name__ == '__main__':
    # Initiate input information
    MRIlogFileLoc, MainLogFileLoc, dcm2nii_path, nii2mnc_path, output_folder, temp_file_folder, MRI_Locations = read_config_file()
    folderPath, subjectID, dateID, scanID = read_input_info(sys.argv[1])

    # Do processing
    folderPath = checkFolderPath(folderPath)
    temp_file_folder = temp_file_folder + '/adniMnc/' + scanID + '/'
    make_sure_path_exists(temp_file_folder)
    otherFiles = removeOtherFilesInFolder(folderPath, ".dcm", temp_file_folder)
    dcm2nii_command = dcm2nii_path + " -a N -e N -p N -o " + temp_file_folder + "/ -v Y " + folderPath
    convert2nii(dcm2nii_command)
    addBackOtherFiles(folderPath,otherFiles,temp_file_folder)
    remove_folder(temp_file_folder)
    mriList = convert2mnc(temp_file_folder,MainLogFileLoc,subjectID,dateID,nii2mnc_path,output_folder)
    searchForMRI(MRIlogFileLoc,output_folder,mriList,MRI_Locations)

# For testing purposes
#dbm = databaseManager(config.libraryFile, config.fMRI_Locations)
#dbm.checkNewFiles()