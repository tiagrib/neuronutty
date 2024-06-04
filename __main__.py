
import sys
from pathlib import Path
from PySide6 import QtWidgets

if __name__ == "__main__":
    # add thirdparty to sys.path
    sys.path.append(str(Path(__file__).resolve().parent / "thirdparty"))
    #import fairmotion
    
    app = QtWidgets.QApplication(sys.argv)
    from nnutty.nnutty import NNutty
    nnutty = NNutty(app)
    nnutty.run()