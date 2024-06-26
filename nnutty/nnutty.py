from pathlib import Path
import sys
import argparse
import logging
from threading import Lock
import matplotlib.pyplot as plt

from PySide6 import QtCore


from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_interpolative_model import FairmotionInterpolativeController
from nnutty.controllers.fairmotion_torch_model_controller import FairmotionMultiController
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
    plotUpdated = QtCore.Signal(int)

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
        self.selected_folder = None
        self.selected_animation = [None, None] # support primary and secondary animations only
        self._skip_reload_animation = [False, False] # support primary and secondary animations only
        self._skip_selected_folder_reload = False

    def add_character(self, character:Character):
        with self.mutex_characters:
            self.characters.clear()
            self.characters.append(character)
        if self.selected_folder is not None and self.get_first_controller().loads_folders():
            self.set_selected_folder(self.selected_folder)
            self._skip_selected_folder_reload = True
        controller_animations = self.get_first_controller().loads_animations()
        for i, anim in enumerate(self.selected_animation):
            if anim is not None and controller_animations > i:
                self.set_selected_animation_file(anim.parent, anim.name, update_plots=True, controller_idx=i)
                self._skip_reload_animation[i] = True
        self.charactersModified.emit()

    def selected_character_invalid(self, controller_type=None):
        return (self.characters is None or 
                len(self.characters) == 0 or
                (controller_type is not None and
                 not isinstance(self.get_first_controller(), controller_type)))

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
    
    def get_first_controller(self):
        character = self.get_first_character()
        if character: return character.controller
        return None

    @QtCore.Slot()
    def add_animfile_character(self):
        logging.info("add_animfile_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=AnimFileController(self, settings=CharacterSettings(args=self.args))))
        
    @QtCore.Slot()
    def add_dual_animfile_character(self):
        logging.info("add_dual_animfile_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=DualAnimFileController(self, settings=CharacterSettings(args=self.args))))

    @QtCore.Slot()
    def add_fairmotion_model_character(self):
        logging.info("add_fairmotion_model_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=FairmotionMultiController(self, settings=CharacterSettings(args=self.args))))
        
    @QtCore.Slot()
    def add_fairmotion_interp_model_character(self):
        logging.info("add_fairmotion_interp_model_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=FairmotionInterpolativeController(self, settings=CharacterSettings(args=self.args))))

    @QtCore.Slot()
    def add_dip_character(self):
        logging.info("add_dip_character()")
        self.add_character(Character(body_model=BodyModel("stick_figure2"),
                                     controller=DIPModelController(self, settings=CharacterSettings(args=self.args))))
    
    @QtCore.Slot()
    def add_nn_character(self, model=None):
        logging.info("add_nn_character()")
        self.add_character(Character(body_model=None,
                                     controller=NNController(self, model, CharacterSettings(args=self.args))))
            
    @QtCore.Slot()
    def add_wave_character(self, model=None):
        logging.info("add_wave_character()")
        self.add_character(Character(body_model=None,
                                     controller=WaveAnimController(self, settings=CharacterSettings(args=self.args))))


    @QtCore.Slot(float, float, float)
    def set_character_world_position(self, x, y, z):
        if self.selected_character_invalid(): return
        logging.info(f"set_character_world_position: [{x}, {y}, {z}]")
        self.get_first_controller().settings.set_world_offset([x, y, z])

    @QtCore.Slot(float)
    def set_character_scale(self, s):
        if self.selected_character_invalid(): return
        logging.info(f"set_character_scale: {s}")
        self.get_first_controller().settings.set_scale(s)


    @QtCore.Slot(bool)
    def show_character_origin(self, show):
        if self.selected_character_invalid(): return
        logging.info(f"show_character_origin: {show}")
        self.get_first_controller().settings.set_show_origin(show)

    @QtCore.Slot(result=bool)
    def get_show_character_origin(self):
        if self.selected_character_invalid(): return False
        return self.get_first_controller().settings.show_origin

    @QtCore.Slot(result=str)
    def get_selected_character_controller_name(self):
        if self.selected_character_invalid(): return ""
        return type(self.get_first_controller()).__name__
    
    @QtCore.Slot(result=str)
    def get_selected_character_controller_type_name(self):
        if self.selected_character_invalid(): return ""
        return self.get_first_controller().ctrl_type.name
    
    @QtCore.Slot(str, str, int)
    def set_selected_animation_file(self, folder, filename, controller_idx=0, update_plots=False):
        if self._skip_reload_animation[controller_idx]:
            self._skip_reload_animation[controller_idx] = False
            return
        if folder is None or filename is None: 
            self.selected_animation[controller_idx] = None
        else:
            self.selected_animation[controller_idx] = Path(folder) / filename
        if (self.selected_character_invalid() or 
            not self.get_first_controller().loads_animations()): return
        self.get_first_controller().load_anim_file(Path(folder) / filename, 
                                                    controller_index=controller_idx, 
                                                    update_plots=update_plots)

    @QtCore.Slot(str, int)
    def set_selected_folder(self, folder, controller_idx=0):
        if self._skip_selected_folder_reload:
            self._skip_selected_folder_reload = False
            return
        self.selected_folder = Path(folder)
        if (self.selected_character_invalid() or 
            not self.get_first_controller().loads_folders()): return
        self.get_first_controller().load_model(self.selected_folder)

    @QtCore.Slot(float)
    def set_fairmotion_model_prediction_ratio(self, ratio=0.9):
        if (self.selected_character_invalid(FairmotionMultiController)): return
        self.get_first_controller().set_prediction_ratio(ratio)
        self.plotUpdated.emit(0)

    @QtCore.Slot(result=float)
    def get_fairmotion_model_prediction_ratio(self):
        if (self.selected_character_invalid(FairmotionMultiController)): return
        return self.get_first_controller().get_prediction_ratio()
    
    @QtCore.Slot(result=str)
    def get_supported_animation_files_extensions(self):
        return "*.pkl,*.bvh,*.npz"
    
    @QtCore.Slot()
    def reset_playback(self):
        if self.selected_character_invalid(): return
        return self.get_first_controller().reset()
    
    @QtCore.Slot(QtCore.QObject, bool)
    def display_all_models(self, folderModel, state:bool):
        if (self.selected_character_invalid() or 
            self.selected_folder is None or
            not self.get_first_controller().loads_folders()): return
        return self.get_first_controller().display_all_models(state, self.selected_folder, folderModel.items)
    
    @QtCore.Slot(float, float)
    def wavectrl_add_joint(self, min_range, max_range):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().add_joint(min_range=min_range, max_range=max_range)

    @QtCore.Slot(float)
    def wavectrl_set_min_range(self, x):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().set_min_range(x)

    @QtCore.Slot(float)
    def wavectrl_set_max_range(self, x):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().set_max_range(x)

    @QtCore.Slot(float)
    def wavectrl_set_min_frequency(self, x):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().set_min_frequency(x)

    @QtCore.Slot(float)
    def wavectrl_set_max_frequency(self, x):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().set_max_frequency(x)

    @QtCore.Slot()
    def wavectrl_randomize_joints(self):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().randomize_joints()

    @QtCore.Slot()
    def wavectrl_reset_joints(self):
        if (self.selected_character_invalid(WaveAnimController)): return
        self.get_first_controller().clear_skeleton()

    @QtCore.Slot()
    def trigger_secondary_animation(self):
        if (self.selected_character_invalid(FairmotionInterpolativeController)): return
        self.get_first_controller().trigger_secondary()
    
    def get_plot_data(self, index=0):
        if self.selected_character_invalid(): return
        return self.get_first_controller().get_plot_data(index)

    def run(self):
        self.win.show()
        self.run_thread(self.viewer.run)
        self.app.exec()
        self.viewer.destroy()
        sys.exit()

    def run_thread(self, func):
        worker = Worker(func)
        self.threadpool.start(worker)