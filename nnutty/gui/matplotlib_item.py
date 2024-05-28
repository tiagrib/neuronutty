from PySide6 import QtCore, QtQuick, QtGui, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import io

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def get_figure_data(self, source, index=0):
        if isinstance(source, QtCore.QObject):
            source = source.get_plot_data(index)
        if source is None:
            return None, 0, 0
        
        x_values, y_values = source
        self.axes.clear()
        self.axes.plot(x_values, y_values)
        self.fig.canvas.draw()
        width, height = self.fig.bbox.size
        buf = io.BytesIO()
        # save figure to buffer
        self.fig.savefig(buf, format='png')
        buf.seek(0) 
        data = buf.read()
        buf.close()
        return data, width, height


class MatplotlibItem(QtQuick.QQuickPaintedItem):
    sizeChanged = QtCore.Signal()

    dpi = 100
    def __init__(self, parent=None):
        super().__init__(parent)
        self._width = 400
        self._height = 300
        self._pixmap = QtGui.QPixmap()
        self.mpl = MplCanvas(self, width=5, height=3, dpi=MatplotlibItem.dpi)
        self.resize_mpl()
        #self.update_figure(([0,1,2,3,4], [10,1,20,3,40]))

    def getDisplayWidth(self):
        return self._width
    
    def getDisplayHeight(self):
        return self._height
    
    def setDisplayWidth(self, width):
        if self._width != width:
            self._width = width
            self.resize_mpl()
            self.sizeChanged.emit()

    def setDisplayHeight(self, height):
        if self._height != height:
            self._height = height
            self.resize_mpl()
            self.sizeChanged.emit()

    display_width = QtCore.Property(int, getDisplayWidth, setDisplayWidth, notify=sizeChanged)
    display_height = QtCore.Property(int, getDisplayHeight, setDisplayHeight, notify=sizeChanged)

    def resize_mpl(self):
        width_in = self._width / MatplotlibItem.dpi
        height_in = self._height / MatplotlibItem.dpi
        self.mpl.fig.set_size_inches(width_in, height_in)

    def paint(self, painter):
        painter.drawPixmap(0, 0, self._pixmap)

    @QtCore.Slot(QtCore.QObject, int)
    def update_figure(self, source, index=0):
        buf, width, height = self.mpl.get_figure_data(source, index)
        if buf is None:
            return
        
        self.setWidth(width)
        self.setHeight(height)
        self._pixmap.loadFromData(buf)
        self.update()
    