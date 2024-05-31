
import sys
from pathlib import Path
from PySide6 import QtWidgets

if __name__ == "__main__":
    # add thirdparty to sys.path
    sys.path.append(Path(__file__).parent / "thirdparty")

    app = QtWidgets.QApplication(sys.argv)
    from nnutty.nnutty import NNutty
    nnutty = NNutty(app)
    nnutty.run()