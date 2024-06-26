import os
import fnmatch
from pathlib import Path
import re
import json
from PySide6 import QtCore, QtGui

from nnutty.data.train_config import TrainConfig

class FolderTreeModel(QtGui.QStandardItemModel):
    folderChanged = QtCore.Signal()
    filterChanged = QtCore.Signal()
    configFilterChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._folder = ''
        self._filter = ''
        self._config_filter = None
        self._negate_config_filter = False
        self.items = []

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

    def get_config_filter(self):
        return self._config_filter
    
    def set_config_filter(self, config_filter):
        if config_filter:
            try:
                # Assuming config_filter is a JSON string from QML
                if config_filter.startswith('!'):
                    self._negate_config_filter = True
                    config_filter = config_filter[1:]
                else:
                    self._negate_config_filter = False
                self._config_filter = json.loads(config_filter)
                self.scanDirectory()
                self.configFilterChanged.emit()
            except json.JSONDecodeError:
                print("Invalid JSON for config_filter")
        else:
            self._config_filter = None

    @QtCore.Slot(int, result=str)
    def getItemData(self, index):
        item = self.item(index)
        if item:
            return item.data(QtCore.Qt.DisplayRole)
        return ''

    folder = QtCore.Property(str, get_folder, set_folder, notify=folderChanged)
    filter = QtCore.Property(str, get_filter, set_filter, notify=filterChanged)
    config_filter = QtCore.Property(str, get_config_filter, set_config_filter, notify=configFilterChanged)

    def check_is_valid_config_filter(self, path):
        if not self._config_filter:
            return True
        config = TrainConfig.from_file(path / 'config.txt')
        config_keys = config.keys()
        for key, check_value in self._config_filter.items():
            if key not in config_keys:
                return self._negate_config_filter
            config_value = str(config[key]).lower()
            if config_value == 'none':
                return self._negate_config_filter
            if ((not self._negate_config_filter and config_value == check_value.lower()) or
                (self._negate_config_filter and config_value != check_value.lower())):
                return True
        return False

    def scanDirectory(self):
        self.clear()
        self.items.clear()

        # check that self._folder is not None and exists
        if not self._folder or not os.path.exists(self._folder):
            return
        
        for _, dirs, _ in os.walk(self._folder):
            for dir in dirs:
                valid_directory = False
                if self._filter.strip() == "":
                    valid_directory = True
                else:
                    for file in (Path(self._folder) / dir).iterdir():
                        if self._filter.startswith('$$'):
                            # regex filter
                            rex = self._filter[2:]
                            reobj = re.compile(rex)
                            if reobj.match(file.name) and self.check_is_valid_config_filter(file.parent):
                                valid_directory = True
                                break
                        else:
                            if file.suffix in self._filter and self.check_is_valid_config_filter(file.parent):
                                valid_directory = True
                                break
                if valid_directory:
                    self.items.append(dir)
                    item = QtGui.QStandardItem(dir)
                    item.setData(dir)
                    self.appendRow(item)

            