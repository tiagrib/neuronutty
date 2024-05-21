from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets, QtQml, QtQuick

from nnutty.viz.nnutty_viewer import NNuttyViewer

ICON_PATH = "resources\\app.ico"

class NNuttyWin():

    def __init__(self, nnutty, parent=None):
        self.nnutty = nnutty

        self.engine = QtQml.QQmlApplicationEngine()
        self.engine.addImportPath(str(Path("nnutty/gui/qml/").resolve()))

        context = self.engine.rootContext()
        context.setContextProperty("nnutty", self.nnutty)

        self.component = QtQml.QQmlComponent(self.engine)
        self.component.loadUrl(QtCore.QUrl("nnutty/gui/qml/nnutty_win.qml"))

    def show(self):
        if self.component.isReady():
            self.component.create()
        else:
            QtCore.qWarning(self.component.errorString())

    def closeEvent(self, event):
        QtWidgets.QWidget.closeEvent(self, event)


    