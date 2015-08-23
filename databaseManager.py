import shelve
import glob
import warnings

class databaseManager:
    d = None

    def __init__(self, l_file):
        self.d = shelve.open(l_file) # Readying database reading and writing. d = database

    def extract_info_from_path(self, scanFolder):
        scanFolder = scanFolder.split("/")
        subjectID = scanFolder[6].split("_")[2]
        scanID = scanFolder[-1]
        return subjectID, scanID

    def scans_already_processed(self, subjectID):
        if subjectID in self.d:
            existingFolders = self.d[subjectID]
        else:
            existingFolders = []
        return existingFolders

    def check_for_new_folders(self, scanFolder):
        newFolderList = []
        subjectID, scanID = self.extract_info_from_path(scanFolder)
        existingFolders = self.scans_already_processed(subjectID)
        existingScanIDs = dict((x.split('/')[-1], x) for x in existingFolders) # Generate a list of S123098, S1309458 folders
        if scanID[0] == "S" and scanID not in existingScanIDs: # If scan folder does not already exist
            existingFolders.append(scanFolder)
            newFolderList.append(scanFolder)
        self.d[subjectID] = existingFolders
        return newFolderList

    def delete_keys(self, scanFolder):
        subjectID, scanID = self.extract_info_from_path(scanFolder)
        existingFolders = self.scans_already_processed(subjectID)
        existingScanIDs = dict((x.split('/')[-1], x) for x in existingFolders) # Generate a list of S123098, S1309458 folders
        if scanID in existingScanIDs.keys(): # If scan value is found in the key, delete it
            existingFolders.remove(existingScanIDs[scanID])
            self.d[subjectID] = existingFolders
        else:
            warnings.warn('scanID ' + scanID + ' not in Database')
        if subjectID in self.d and not self.d[subjectID]: # If no more values to key, delete key
            del self.d[subjectID]
        self.d.sync()

    def generate_list_of_folders(self, dicomFolder):
        list = []
        listOfSubjects = glob.glob(dicomFolder + "/*/*_S_*")
        for possibleFolder in ["/MRI/fMRI","/MRI/rsfmri","/MRI/rsfmri/Resting_State_fMRI","/MRI/fMRI/Resting_State_fMRI","/MRI/rsfmri/Extended_Resting_State_fMRI","/MRI/rsfmri/epi_2s_resting_state"]:
            for x in listOfSubjects:
                listOfScans = glob.glob(x + possibleFolder + "/*/S*")
                if listOfScans:
                    [list.append(i) for i in listOfScans]
        return list

    def check_new_files(self, dicomFolder): # For each raw DICOM folder database (e.g. /data/data02/ADNI/raw/)
        newFolderList = []
        list = self.generate_list_of_folders(dicomFolder)
        for x in list: # For each scanFolder
            folderList = self.check_for_new_folders(x)
            [newFolderList.append(i) for i in folderList]
        self.d.sync()
        return newFolderList

    def sync(self):
        self.d.sync()

    def close(self):
        self.d.close()

# For testing purposes
'''
newFolderList = []
dbm = databaseManager("/home/wang/Documents/bin2/20140422_adniDatabase.lst")
list = dbm.generate_list_of_folders("/data/data02/ADNI/raw")
for x in list: # For each scanFolder
    folderList = dbm.check_for_new_folders(x)
    [newFolderList.append(i) for i in folderList]
'''