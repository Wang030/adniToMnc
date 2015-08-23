import os

__author__ = 'wang'


class ProcessingList:
    folderList = None

    def __init__(self):
        self.folderList = []  # Readying database reading and writing. d = database

    def check(self, folder):
        data = None
        i = os.walk(folder).next()
        if not i[1]:  # If no subfolder, continue, else fail. Make sure that it is at the deepest level
            data = i[2][0].split("_")    # ['ADNI', '130', 'S', '2391', 'MR', 'Resting', 'State', 'fMRI', 'br', 'raw', '20110622150204096', '1', 'S112049', 'I240902.dcm']
            if len(data) >= 10:  # Make sure it's a proper DCM file
                data.append(i[0])  # i - ['<path>','<folders in the path>','<files in the path>']
        return data

    def add(self, folder):
        info = self.check(folder)
        if info is not None:
            self.folderList.append(info)

    def data(self):
        return self.folderList