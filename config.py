##Configuration file for conversion of dcm to fMRI and match with corresponding MRI

####### Configuration for run.py #############
#Number of processes to be used for the operation. Usually the number of cores in the system. [0 - 12]. [Put 0 for Auto]
numberOfProcesses = 0
#Data File Folder - Folder which contain the dcm files.
fMRI_Locations = ["/data/data02/ADNI/raw","/data/data02/ADNI/new_raw"]
#Folder for the output of Data - Final fMRI and MRI files will be in this folder
output_folder = "/data/data03/wang/input/20140805_ADNI/raw/"

####### Configuration for dcmTomnc.py ########
#Location of the MRIlog file - only to log any missing MRI files.
MRIlogFileLoc = "/home/wang/Documents/bin2/20140805_MRI.log"
#Location of the log file - MAIN Log.
logFileLoc = "/home/wang/Documents/bin2/20140805_run.log"
#Location of the executable dcm2nii path
dcm2nii_path = "/home/sulantha/bin/references/dcm2nii"
#Location of the executable nii2mnc path
nii2mnc_path = "/home/sulantha/bin/references/nii2mnc"
#Location of the temporary folder to have the xml files while processing the dcm files.
#Interruption in the program may leave the moved xml files here.
# It will not be moved back to the respective folder if the program interrupts.
temp_file_folder = "/data/data02/wang/temp/"
#Location of the MRI files. Specify subject folders.
MRI_Locations = ["/data/data02/ADNI/converted/*/", "/data/data02/ADNI/toms_converted/*/"]

####### Configuration for databaseManager.py ########
#Location of database library
libraryFile = "/home/wang/Documents/bin2/20140805_adniDatabase.lst"