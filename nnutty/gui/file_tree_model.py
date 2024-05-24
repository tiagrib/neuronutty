import os
import fnmatch
from PySide6 import QtCore, QtGui

class FileTreeModel(QtGui.QStandardItemModel):
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
        
        for root, dirs, files in os.walk(self._folder):
            for extension in self._filter.split(','):
                for file in fnmatch.filter(files, extension):
                    item = QtGui.QStandardItem(file)
                    self.appendRow(item)