

from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_torch_model_controller import FairmotionModelController, FairmotionMultiController
from fairmotion.ops import conversions
from fairmotion.core.motion import Pose


class FairmotionInterpolativeController(FairmotionMultiController):
    def __init__(self, nnutty, 
                 model_path:str = None, 
                 settings:CharacterSettings = None,
                 parent=None):
        self.animctrl1 = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        self.animctrl2 = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        self.fimctrl = FairmotionInterpolativeModelController(nnutty,
                                                              model_path,
                                                              settings=CharacterSettings.copy(settings),
                                                              animctrl=self.animctrl1,
                                                              animctrl2=self.animctrl2,
                                                              parent=self)
        super().__init__(nnutty,
                         model_path=model_path,
                         settings=settings,
                         parent=parent,
                         fmctrl=self.fimctrl,
                         animctrl=self.animctrl1,
                         )
        self.ctrls.append(self.animctrl2)
        self.reposition_subcontrollers()
        
    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        if controller_index == 0:
            FairmotionMultiController.load_anim_file(self, filename, controller_index, update_plots)
        else:
            self.animctrl2.load_anim_file(filename)
            self.fimctrl.preprocess_secondary()

    def trigger_secondary(self):
        print("SECONDARY")

class FairmotionInterpolativeModelController(FairmotionModelController):
    def __init__(self, nnutty,  model_path:str = None, 
                 settings:CharacterSettings = None,
                 animctrl = None,
                 animctrl2 = None,
                 parent=None):
        if animctrl2 is None:
            animctrl2 = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        self.anim_file_ctrl2 = animctrl2
        super().__init__(nnutty, model_path=model_path, settings=settings, animctrl=animctrl, parent=parent)
        self.preprocessed_secondary_motion = None
        self.src_len = 5
        self.dst_len = 5
    
    def preprocess_secondary(self):
        if self.anim_file_ctrl2.motion is None:
            return
        
        cached = self._get_cached(1)
        if cached:
            self.preprocessed_secondary_motion = cached
        else:
            self.preprocessed_secondary_motion = conversions.R2T(self.anim_file_ctrl2.motion.rotations())

    def preprocess_motion(self):
        if self.anim_file_ctrl.motion is None:
            return
        
        cached = self._get_cached(0)
        if cached:
            self.preprocessed_motion = cached
        else:
            self.preprocessed_motion = conversions.R2T(self.anim_file_ctrl.motion.rotations())

    def recompute_prediction(self):
        if self.anim_file_ctrl.motion is None:
            return
        
        if self.preprocessed_motion is None:
            self.preprocess_motion()
        
        computed_motion = self.preprocessed_motion

        self.computed_poses = []
        for i in range(self.total_frames):
            self.computed_poses.append(Pose(self.anim_file_ctrl.motion.skel, computed_motion[i]))

        self._cache_computed_poses(0)