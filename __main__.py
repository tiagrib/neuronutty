
import sys
from PySide6 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    from nnutty.nnutty import NNutty
    nnutty = NNutty(app)
    nnutty.run()