import sys
import argparse
from threading import Lock

from PySide6 import QtGui, QtCore, QtWidgets

from nnutty.gui.nnutty_win import NNuttyWin
from nnutty.viz.nnutty_viewer import NNuttyViewer
from nnutty.controllers.character import BodyModel, Character
from nnutty.controllers.anim_file_controller import BVHFileController
from nnutty.controllers.nn_controller import NNController

def parse_args():
    parser = argparse.ArgumentParser(description="Visualize BVH file with block body")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--thickness", type=float, default=1.0,help="Thickness (radius) of character body")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--axis-up", type=str, choices=["x", "y", "z"], default="y")
    parser.add_argument("--axis-face", type=str, choices=["x", "y", "z"], default="z")
    parser.add_argument("--camera-position", nargs="+", type=float, required=False, default=(0.0, 15.0, 20.0))
    parser.add_argument("--camera-origin", nargs="+", type=float, required=False, default=(0, 5.0, 0.0))
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

class NNutty(QtCore.QObject):
    def __init__(self):
        super().__init__()

        self.args = parse_args()

        #app = QtWidgets.QApplication(sys.argv)
        self.app = QtWidgets.QApplication(sys.argv)
        #self.app = QtWidgets.QApplication(sys.argv)
        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.win = NNuttyWin(self)

        self.args.scale = 0.05
        self.args.thickness = 5.0
        self.viewer = NNuttyViewer(self)

        self.mutex_characters = Lock()
        self.characters = []

    @QtCore.Slot()
    def add_bvh_character(self):
        with self.mutex_characters:
            self.characters.clear()
            filename = "C:/repo/mocap/accad_motion_lab/Female1_bvh/Female1_A03_SwingT2.bvh"
            self.characters.append(Character(body_model=BodyModel("stick_figure2"),
                                             controller=BVHFileController(filename=filename, 
                                                                          v_front=self.args.axis_face, 
                                                                          v_up=self.args.axis_up, 
                                                                          scale=self.args.scale)))
    
    @QtCore.Slot()
    def add_nn_character(self, model=None):
        with self.mutex_characters:
            self.characters.clear()
            self.characters.append(Character(body_model=None,
                                             controller=NNController(model, 
                                                                     v_front=self.args.axis_face, 
                                                                     v_up=self.args.axis_up, 
                                                                     scale=self.args.scale)))
            
    @QtCore.Slot(float, float, float)
    def set_character_world_position(self, x, y, z):
        print("Setting character world position: ", x, y, z)
        if self.characters:
            with self.mutex_characters:
                self.characters[0].controller.settings.set_world_offset([x, y, z])

    @QtCore.Slot(bool)
    def show_character_origin(self, show):
        if self.characters:
            with self.mutex_characters:
                self.characters[0].controller.settings.set_show_origin(show)

    def get_characters(self):
        char_enum = None
        with self.mutex_characters:
            char_enum = enumerate(self.characters)
        return char_enum

    def run(self):
        self.win.show()
        self.run_thread(self.viewer.run)
        self.app.exec()
        self.viewer.destroy()
        sys.exit()

    def run_thread(self, func):
        worker = Worker(func)
        self.threadpool.start(worker)