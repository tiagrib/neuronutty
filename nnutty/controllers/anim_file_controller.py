from enum import Enum
import logging

from fairmotion.data import bvh, asfamc, amass_dip

from nnutty.controllers.cached_anim_controller import CachedAnimController
from nnutty.controllers.multi_anim_controller import MultiAnimController
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings

class DualAnimFileController(MultiAnimController):
    def __init__(self, nnutty, 
                 settings:CharacterSettings = None,
                 parent=None):
        super().__init__(nnutty,
                         ctrls=[AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self),
                                AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)],
                         settings=settings,
                         parent=parent)
        self.ctrl_type = CharCtrlType.DUAL_ANIM_FILE
        
    def loads_animations(self):
        return True

    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        assert(controller_index < len(self.ctrls))
        self.ctrls[controller_index].load_anim_file(filename, controller_index=controller_index, update_plots=update_plots)
        self.reset()


class AnimFileController(CachedAnimController):
    def __init__(self,
                 nnutty,
                 filename:str = None,
                 settings:CharacterSettings = None,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.ANIM_FILE, settings=settings, parent=parent)
        self.caches = {}
        self.plot_data_cache = {}
        self.filename = None
        self.load_anim_file(filename)

    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        if filename in self.caches:
            self.motion = self.caches[filename]
            self.filename = filename
        else:        
            motion = None
            if filename:
                if not isinstance(filename, list):
                    if filename.suffix.lower() == ".bvh":
                        motion = bvh.load(file=filename)
                        motion.name = filename.name
                    elif filename.suffix.lower() in [".pkl", ".npz"]:
                        motion = amass_dip.load(filename, file_type=filename.suffix.lower()[1:])
                        motion.name = filename.name
                elif (isinstance(filename, list) and len(filename) == 2 and 
                        filename[0] is not None and filename[1] is not None and
                        filename[0].lower().endswith(".asf") and filename[0].lower().endswith(".asc")):
                    motion = asfamc.load(file=filename[0], motion=filename[1])

            if motion:
                self.digest_fairmotion(motion)
                logging.info(f"Loaded animation file: '{filename}'")
                self.caches[filename] = self.motion
                self.filename = filename
        if self.motion:
            if update_plots or controller_index == 0:
                self.nnutty.plot1Updated.emit()
            if update_plots or controller_index == 1:
                self.nnutty.plot2Updated.emit()

    def get_plot_data(self, index=0):
        if self.filename in self.plot_data_cache:
            res = self.plot_data_cache[self.filename]
        else:
            res = super().get_plot_data(index)
            if res is not None:
                self.plot_data_cache[self.filename] = res
        return res

        

