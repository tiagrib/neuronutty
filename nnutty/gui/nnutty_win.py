from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtQml

from nnutty.controllers.character_controller import CharCtrlTypeWrapper
from nnutty.gui.file_tree_model import FileTreeModel
from nnutty.gui.folder_tree_model import FolderTreeModel
from nnutty.gui.matplotlib_item import MatplotlibItem

ICON_PATH = "resources\\app.ico"

class NNuttyWin():

    def __init__(self, nnutty, parent=None):
        self.nnutty = nnutty
        QtCore.QCoreApplication.setOrganizationName("TiagoRibeiro")
        QtCore.QCoreApplication.setApplicationName("NeuroNutty")
        self.engine = QtQml.QQmlApplicationEngine()
        self.engine.addImportPath(str(Path("nnutty/gui/qml/").resolve()))

        context = self.engine.rootContext()
        context.setContextProperty("nnutty", self.nnutty)
        self.charCtrlTypeWrapper = CharCtrlTypeWrapper()
        context.setContextProperty("CharCtrlType", self.charCtrlTypeWrapper)

        QtQml.qmlRegisterType(FileTreeModel, 'NNutty', 1, 0, 'FileTreeModel')
        QtQml.qmlRegisterType(FolderTreeModel, 'NNutty', 1, 0, 'FolderTreeModel')
        QtQml.qmlRegisterType(MatplotlibItem, 'Matplotlib', 1, 0, 'MatplotlibItem')

        self.component = QtQml.QQmlComponent(self.engine)
        self.component.loadUrl(QtCore.QUrl("nnutty/gui/qml/nnutty_win.qml"))

    def show(self):
        if self.component.isReady():
            self.component.create()
        else:
            QtCore.qWarning(self.component.errorString())

    def closeEvent(self, event):
        QtWidgets.QWidget.closeEvent(self, event)


    