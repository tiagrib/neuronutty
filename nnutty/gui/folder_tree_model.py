import os
import fnmatch
from pathlib import Path
from PySide6 import QtCore, QtGui

class FolderTreeModel(QtGui.QStandardItemModel):
    folderChanged = QtCore.Signal()
    filterChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folder = ''
        self._filter = ''

    def get_folder(self):
        return self._folder
    
    def set_folder(self, folder):
        self._folder = folder
        self.scanDirectory()
        self.folderChanged.emit()
    
    def get_filter(self):
        return self._filter
    
    def set_filter(self, filter):
        self._filter = filter
        self.scanDirectory()
        self.folderChanged.emit()

    @QtCore.Slot(int, result=str)
    def getItemData(self, index):
        item = self.item(index)
        if item:
            return item.data(QtCore.Qt.DisplayRole)
        return ''

    folder = QtCore.Property(str, get_folder, set_folder, notify=folderChanged)
    filter = QtCore.Property(str, get_filter, set_filter, notify=filterChanged)

    def scanDirectory(self):
        self.clear()

        # check that self._folder is not None and exists
        if not self._folder or not os.path.exists(self._folder):
            return
        
        for _, dirs, _ in os.walk(self._folder):
            for dir in dirs:
                valid_directory = False
                if self._filter.strip() == "":
                    valid_directory = True
                else:
                    for _, _, files in os.walk(Path(self._folder) / dir ):
                        for extension in self._filter.split(','):
                            for file in fnmatch.filter(files, extension):
                                found_valid_files = True
                                break
                            if found_valid_files:
                                break
                        if found_valid_files:
                            break
                if valid_directory:
                    item = QtGui.QStandardItem(dir)
                    item.setData(dir)
                    self.appendRow(item)

            