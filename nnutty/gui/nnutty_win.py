from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

from nnutty.viz.nnutty_viewer import NNuttyViewer

ICON_PATH = "resources\\app.ico"

class NNuttyWin(QtWidgets.QMainWindow):

    def __init__(self, parent=None, args=None):
        super().__init__(parent)

        if Path(ICON_PATH).exists():
            icon = QtGui.QIcon(ICON_PATH)
            self.setWindowIcon(icon)

        self.setWindowTitle("NeuroNutty")
        self.settings = QtCore.QSettings("Nutty", "NeuroNutty")
        self._setup_menus()

        # Layouts
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.grid = QtWidgets.QGridLayout(self.main_widget)
        self.grid.setContentsMargins(5, 5, 5, 5)

        self.grp_settings = self._add_group(0, 0, 1, 1, title="Settings")
        self.grp_character = self._add_group(0, 0, 1, 1, title="Character")
        self.grp_charctrl = self._add_group(1, 0, 1, 1, title="Character Controls")
        self.grp_controller = self._add_group(0, 1, 2, 1, title="Controller Settings")

        self._setup_grp_settings()
        self._setup_grp_character()
        self._setup_grp_charctrl()
        self._setup_grp_controller()

    def _add_group(self, row, col, rowSpan, colSpan, title=""):
        groupBox = QtWidgets.QGroupBox(title=title)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(groupBox.sizePolicy().hasHeightForWidth())
        groupBox.setSizePolicy(sizePolicy)
        self.grid.addWidget(groupBox, row, col, rowSpan, colSpan)
        return groupBox
    
    def _setup_grp_settings(self):
        pass

    def _setup_grp_character(self):
        pass

    def _setup_grp_charctrl(self):
        pass

    def _setup_grp_controller(self):
        pass
    
    def _setup_menus(self):
        pass
        # create a "File" menu and add an "Export CSV" action to it
        #file_menu = QtWidgets.QMenu("File", self)
        #self.menuBar().addMenu(file_menu)

        #load_action = QtGui.QAction("Load Project", self)
        #load_action.triggered.connect(self.get_project_path)
        #file_menu.addAction(load_action)

        #save_action = QtGui.QAction("Save Project", self)
        #save_action.triggered.connect(self.save_project)
        #file_menu.addAction(save_action)


    def closeEvent(self, event):
        QtWidgets.QWidget.closeEvent(self, event)


    