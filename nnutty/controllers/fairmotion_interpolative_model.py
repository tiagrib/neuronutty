

import numpy as np
from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_torch_model_controller import FairmotionModelController, FairmotionMultiController
from fairmotion.ops import conversions
from fairmotion.core.motion import Pose

BASE_MOTION_CACHE = 10
SECONDARY_MOTION_CACHE = 20
BASE_POSES_CACHE = 0
SECONDARY_POSES_CACHE = 1

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
            self.animctrl1.load_anim_file(filename, controller_index=controller_index)
            self.fimctrl.recompute_base_animation()
            self.reset()
        else:
            self.animctrl2.load_anim_file(filename, controller_index=controller_index)
            self.fimctrl.preprocess_secondary()

    def trigger_secondary(self):
        print("SECONDARY")
        self.fimctrl.trigger_transition()

    def load_model(self, model_path:str):
        self.fimctrl.load_model(model_path, recompute=False)

    def loads_animations(self):
        return 2
    
    def get_cur_time(self):
        return self.fimctrl.get_cur_time()

class FairmotionInterpolativeModelController(FairmotionModelController):
    def __init__(self, nnutty,  model_path:str = None, 
                 settings:CharacterSettings = None,
                 animctrl = None,
                 animctrl2 = None,
                 parent=None):
        if animctrl2 is None:
            animctrl2 = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        self.anim_file_ctrl2 = animctrl2
        self.queue_secondary_loading = False
        super().__init__(nnutty, model_path=model_path, settings=settings, animctrl=animctrl, parent=parent)
        self.total_time = 0.0
        self.transition_frame = None
        self.preprocessed_secondary_motion = None
        self.total_secondary_frames = 0
        self.src_len = 5
        self.dst_len = 5
    
    def preprocess_secondary(self):
        if self.anim_file_ctrl2.motion is None:
            return
        if self.anim_file_ctrl2.fps != self.anim_file_ctrl.fps:
            if self.anim_file_ctrl.end_time == 0.0:
                self.queue_secondary_loading = True
                return
            print("FPS mismatch between base and secondary animations")
            self.preprocessed_secondary_motion = None
            return
        
        cached = self._get_cached(SECONDARY_MOTION_CACHE, key2=self.anim_file_ctrl2.filename)
        if cached is not None:
            print("Using cached secondary animation")
            self.preprocessed_secondary_motion = cached
        else:
            print("Preprocessing secondary animation")
            self.total_secondary_frames = self.anim_file_ctrl2.motion.num_frames()
            self.preprocessed_secondary_motion = conversions.R2T(self.anim_file_ctrl2.motion.rotations())
            self._add_cache(self.preprocessed_secondary_motion, SECONDARY_MOTION_CACHE, key2=self.anim_file_ctrl2.filename)
            computed_secondary = []
            for i in range(self.total_secondary_frames):
                computed_secondary.append(Pose(self.anim_file_ctrl2.motion.skel, self.preprocessed_secondary_motion[i]))
            self._add_cache(computed_secondary, SECONDARY_POSES_CACHE, key2=self.anim_file_ctrl2.filename)

    def preprocess_base(self):
        if self.anim_file_ctrl.motion is None:
            return
        
        cached = self._get_cached(BASE_MOTION_CACHE)
        if cached is not None:
            print("Using cached base animation")
            self.preprocessed_motion = cached
        else:
            print("Preprocessing base animation")
            self.preprocessed_motion = conversions.R2T(self.anim_file_ctrl.motion.rotations())
            self._add_cache(self.preprocessed_motion, BASE_MOTION_CACHE)
        if self.queue_secondary_loading:
            self.preprocess_secondary()
            self.queue_secondary_loading = False

    def recompute_base_animation(self):
        print("Recomputing base animation")
        self.preprocess_base()
        self.total_frames = self.anim_file_ctrl.motion.num_frames()
        self.total_time = self.anim_file_ctrl.motion.length()
        self.transition_frame = None
        cached = self._get_cached(BASE_POSES_CACHE)
        if cached is not None:
            print("Using cached poses")
            self.computed_poses = cached
        else:
            print("Computing poses")
            self.computed_poses = []
            for i in range(self.total_frames):
                self.computed_poses.append(Pose(self.anim_file_ctrl.motion.skel, self.preprocessed_motion[i]))
            self._cache_computed_poses(BASE_POSES_CACHE)
        

    def trigger_transition(self):
        if self.preprocessed_secondary_motion is None:
            print("Secondary motion not preprocessed")
            return
        self.transition_frame = self.anim_file_ctrl.motion.time_to_frame(self.anim_file_ctrl.cur_time)
        self.transition_to_frame = self.anim_file_ctrl2.motion.time_to_frame(self.anim_file_ctrl2.cur_time)
        
        self.computed_poses = self._get_cached(BASE_POSES_CACHE)[:self.transition_frame]
        self.computed_poses.extend(self._get_cached(SECONDARY_POSES_CACHE, key2=self.anim_file_ctrl2.filename)[self.transition_to_frame:])
        self.total_frames = len(self.computed_poses)
        self.total_time = self.total_frames / self.anim_file_ctrl.fps

    def advance_time(self, dt, params=None):
        if self.computed_poses:
            try:
                curr_frame = int(self.cur_time * self.anim_file_ctrl.fps + 1e-05)
                self.cur_time += dt
                if self.cur_time > self.total_time:
                    self.cur_time = 0.0
                self.pose = self.computed_poses[curr_frame]
                if self.transition_frame is not None and curr_frame >= self.transition_frame:
                    self.settings.color = np.array([173, 130, 50, 255]) / 255.0  # orange-red
                else:
                    self.settings.color = np.array([85, 160, 173, 255]) / 255.0  # blue
            except Exception as e:
                print(f"Error computing pose: {e}")
