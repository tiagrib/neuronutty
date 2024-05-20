import sys
import argparse
from PySide6 import QtWidgets, QtCore

from nnutty.gui.nnutty_win import NNuttyWin
from nnutty.viz.nnutty_viewer import NNuttyViewer

def parse_args():
    parser = argparse.ArgumentParser(description="Visualize BVH file with block body")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--thickness", type=float, default=1.0,help="Thickness (radius) of character body")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--axis-up", type=str, choices=["x", "y", "z"], default="y")
    parser.add_argument("--axis-face", type=str, choices=["x", "y", "z"], default="z")
    parser.add_argument("--camera-position", nargs="+", type=float, required=False, default=(0.0, 5.0, 5.0))
    parser.add_argument("--camera-origin", nargs="+", type=float, required=False, default=(0, 0.0, 0.0))
    parser.add_argument("--hide-origin", action="store_false")
    parser.add_argument("--render-overlay", action="store_false")
    args = parser.parse_args()

    assert len(args.camera_position) == 3 and len(args.camera_origin) == 3, (
        "Provide x, y and z coordinates for camera position/origin like "
        "--camera-position x y z"
    )
    return args

class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)

class NNutty:
    def __init__(self):
        self.args = parse_args()
        self.app = QtWidgets.QApplication(sys.argv)
        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.win = NNuttyWin(args=self.args)

        self.args.scale = 0.05
        self.args.thickness = 5.0
        self.viewer = NNuttyViewer(args=self.args)
        self.viewer.add_bvh_character("C:/repo/mocap/accad_motion_lab/Female1_bvh/Female1_A03_SwingT2.bvh", self.args)

    def run(self):
        self.win.show()
        self.run_thread(self.viewer.run)
        self.app.exec()
        self.viewer.destroy()
        sys.exit()

    def run_thread(self, func):
        worker = Worker(func)
        self.threadpool.start(worker)