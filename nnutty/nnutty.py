from pathlib import Path
import sys
import argparse
import logging
from threading import Lock

from PySide6 import QtCore

from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_torch_model_controller import FairmotionDualController
from nnutty.controllers.wave_controller import WaveAnimController
from nnutty.gui.nnutty_win import NNuttyWin
from nnutty.gui.viz.nnutty_viewer import NNuttyViewer
from nnutty.controllers.character import BodyModel, Character
from nnutty.controllers.anim_file_controller import AnimFileController, DualAnimFileController
from nnutty.controllers.nn_controller import NNController
from nnutty.controllers.dip_controller import DIPModelController

def parse_args():
    parser = argparse.ArgumentParser(description="Visualize BVH file with block body")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--thickness", type=float, default=1.0,help="Thickness (radius) of character body")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--axis-up", type=str, choices=["x", "y", "z"], default="y")
    parser.add_argument("--axis-face", type=str, choices=["x", "y", "z"], default="z")
    parser.add_argument("--camera-position", nargs="+", type=float, required=False, default=(0.0, 5.0, 20.0))
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

class NNutty(QtCore.QObject):
    charactersModified = QtCore.Signal()

    def __init__(self, app):
        super().__init__()

        logging.basicConfig(level=logging.INFO)

        self.args = parse_args()

        #app = QtWidgets.QApplication(sys.argv)
        self.app = app
        #self.app = QtWidgets.QApplication(sys.argv)
        self.threadpool = QtCore.QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.win = NNuttyWin(self)

        self.args.scale = 1.0
        self.args.thickness = 1.0
        self.viewer = NNuttyViewer(self)

        self.mutex_characters = Lock()
        self.characters = []
        self.selected_animation = None

    def add_character(self, character:Character):
        with self.mutex_characters:
            self.characters.clear()
            self.characters.append(character)
        if self.selected_animation is not None and self.get_first_character().controller.loads_animations():
            self.set_selected_animation_file(self.selected_animation.parent, self.selected_animation.name)
        self.charactersModified.emit()

    def selected_character_invalid(self):
        return self.characters is None or len(self.characters) == 0

    def get_characters(self):
        char_enum = None
        with self.mutex_characters:
            char_enum = enumerate(self.characters)
        return char_enum
    
    def get_first_character(self):
        character = None
        with self.mutex_characters:
            character = self.characters[0]
        return character

    @QtCore.Slot()
    def add_animfile_character(self):
        logging.info("add_animfile_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=AnimFileController(settings=CharacterSettings(args=self.args))))
        
    @QtCore.Slot()
    def add_dual_animfile_character(self):
        logging.info("add_dual_animfile_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=DualAnimFileController(settings=CharacterSettings(args=self.args))))

    @QtCore.Slot()
    def add_fairmotion_model_character(self):
        logging.info("add_fairmotion_model_character()")
        model = "C:/repo/DIP/models/test1/best.model"
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=FairmotionDualController(model=model, settings=CharacterSettings(args=self.args))))

    @QtCore.Slot()
    def add_dip_character(self):
        logging.info("add_dip_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=DIPModelController(settings=CharacterSettings(args=self.args))))
    
    @QtCore.Slot()
    def add_nn_character(self, model=None):
        logging.info("add_nn_character()")
        self.add_character(Character(body_model=None,
                                     controller=NNController(model, CharacterSettings(args=self.args))))
            
    @QtCore.Slot()
    def add_wave_character(self, model=None):
        logging.info("add_wave_character()")
        self.add_character(Character(body_model=None,
                                     controller=WaveAnimController(model, CharacterSettings(args=self.args))))

    @QtCore.Slot(float, float, float)
    def set_character_world_position(self, x, y, z):
        if self.selected_character_invalid(): return
        logging.info(f"set_character_world_position: [{x}, {y}, {z}]")
        self.get_first_character().controller.settings.set_world_offset([x, y, z])

    @QtCore.Slot(bool)
    def show_character_origin(self, show):
        if self.selected_character_invalid(): return
        logging.info(f"show_character_origin: {show}")
        self.get_first_character().controller.settings.set_show_origin(show)

    @QtCore.Slot(result=bool)
    def get_show_character_origin(self):
        if self.selected_character_invalid(): return False
        return self.get_first_character().controller.settings.show_origin

    @QtCore.Slot(result=int)
    def get_selected_character_controller_type_value(self):
        if self.selected_character_invalid(): return -1
        return self.get_first_character().controller.ctrl_type.value
    
    @QtCore.Slot(result=str)
    def get_selected_character_controller_type_name(self):
        if self.selected_character_invalid(): return None
        return self.get_first_character().controller.ctrl_type.name
    
    @QtCore.Slot(str, str, int)
    def set_selected_animation_file(self, folder, filename, controller_idx=0):
        if folder is None or filename is None: 
            self.selected_animation = None
        else:
            self.selected_animation = Path(folder) / filename
        if (self.selected_character_invalid() or 
            not self.get_first_character().controller.loads_animations()): return
        self.get_first_character().controller.load_anim_file(self.selected_animation, controller_idx)

    def run(self):
        self.win.show()
        self.run_thread(self.viewer.run)
        self.app.exec()
        self.viewer.destroy()
        sys.exit()

    def run_thread(self, func):
        worker = Worker(func)
        self.threadpool.start(worker)