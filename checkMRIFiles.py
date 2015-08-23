import os
import config
import glob
import subprocess

__author__ = 'wang'
folders = config.fMRI_Locations
MRIlogFileLoc = config.MRIlogFileLoc
MRI_Locations = config.MRI_Locations

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

def searchForMRI(scanFolder):
    MRIlogFile = open(MRIlogFileLoc, 'a+')
    info = scanFolder.split("/")
    subjectID = info[7].split("_")[2] # subjectID from dirname
    #dateOne = [x.find("-") for x in info]
    #dateOne = [i for i,x in enumerate(dateOne) if x != -1]
    #date = info[dateOne[0]]
    #date2 = os.walk(scanFolder)[2][0].split("_")[10]
    foundMRI = False
    for location in MRI_Locations:
        if not foundMRI:
            subjectMRIListWithDates = getCorrespondingMRI(location, subjectID)
            if len(subjectMRIListWithDates) is not 0:
                foundMRI = True
    if not foundMRI:
        MRIlogFile.write(subjectID + "\n")
    MRIlogFile.close()

if __name__ == '__main__':
    foldersList = []
    for dicomFolder in folders: # For each raw DICOM folder database (e.g. /data/data02/ADNI/raw/)
        dicomFolder += "/" # Full-proof it
        for diagnosisFolder in os.listdir(dicomFolder): # For each baseline diagnosis (e.g. /data/data02/ADNI/raw/MCI/)
            diagnosisFolder = dicomFolder + "/" + diagnosisFolder
            if os.path.isdir(diagnosisFolder):
                for subjectID in os.listdir(diagnosisFolder): # For each subject folder (e.g. /data/data02/ADNI/raw/MCI/002_S_2043/)
                    possibleFolders = ["/MRI/fMRI","/MRI/rsfmri","/MRI/rsfmri/Resting_State_fMRI","/MRI/fMRI/Resting_State_fMRI","/MRI/rsfmri/Extended_Resting_State_fMRI","/MRI/rsfmri/epi_2s_resting_state"]
                    for possibleFolder in possibleFolders:
                        possibleFolder = diagnosisFolder + "/" + subjectID + "/" + possibleFolder # For each possible folder (e.g. /data/data02/ADNI/raw/EMCI/002_S_2043/MRI/rsfmri/)
                        if os.path.isdir(possibleFolder) and not os.listdir(possibleFolder) == []: # If is directory and not empty
                            for dateFolder in os.listdir(possibleFolder): # For each date folder (e.g. /data/data02/ADNI/raw/EMCI/002_S_2043/MRI/rsfmri/2010-12-08_11_31_20.0)
                                dateFolder = possibleFolder + "/" + dateFolder
                                if os.path.isdir(dateFolder):
                                    for f in os.listdir(dateFolder): # For each scan folder (e.g. /data/data02/ADNI/raw/EMCI/002_S_2043/MRI/rsfmri/2010-12-08_11_31_20.0/S96108)
                                        scanFolder = dateFolder + "/" + f
                                        if os.path.isdir(scanFolder) and f[0] == "S" and f not in foldersList: # If scan folder does not already exist
                                            foldersList.append(scanFolder)
    for folder in foldersList:
        searchForMRI(folder)