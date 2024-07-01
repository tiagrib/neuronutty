

import numpy as np
from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.cached_anim_controller import CachedAnimController
from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_torch_model_controller import ACTIVE_COLOR, INACTIVE_COLOR, FairmotionModelController, FairmotionMultiController
import torch
from fairmotion.ops import conversions
from fairmotion.core.motion import Pose
from fairmotion.tasks.motion_prediction import generate
from fairmotion.ops import math as motion_math
from nnutty.util.plot_data import get_plot_data_from_poses

BASE_MOTION_CACHE = 10
SECONDARY_MOTION_CACHE = 20

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
        self.linctrl = CachedAnimController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        super().__init__(nnutty,
                         model_path=model_path,
                         settings=settings,
                         parent=parent,
                         fmctrl=self.fimctrl,
                         animctrl=self.animctrl1,
                         )
        self.ctrls.append(self.animctrl2)
        self.ctrls.append(self.linctrl)
        self.animctrl1.name = "Base\nMotion"
        self.animctrl2.name = "Target\nMotion"
        self.fimctrl.name = "Neural\nTransition"
        self.linctrl.name = "Linear\nTransition"
        self.reposition_subcontrollers()
        
    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        if controller_index == 0:
            self.animctrl1.load_anim_file(filename, controller_index=controller_index, update_plots=True)
            self.fimctrl.preprocess_base()
            self.fimctrl.reset_linear_transition(self.linctrl)
            self.nnutty.plotUpdated.emit(2)
        else:
            self.animctrl2.load_anim_file(filename, controller_index=controller_index, update_plots=True)
            self.fimctrl.preprocess_secondary()
        self.reset()

    def trigger_secondary(self):
        print("SECONDARY")
        self.fimctrl.trigger_transition(self.linctrl)

    def load_model(self, model_path:str):
        self.fimctrl.load_model(model_path, recompute=False)

    def loads_animations(self):
        return 2
    
    def get_cur_time(self):
        return self.fimctrl.get_cur_time()
    
    def get_plot_data(self, index, no_cache=False):
        return self.ctrls[[0, 2, 1, 3][index]].get_plot_data(no_cache=index==2)
    
    def get_ground_point(self, pose):
        return self.fimctrl.get_ground_point(pose)
    
    def set_fade_in_max_frames(self, frames:int):
        self.fimctrl.transition_fade_frames = frames
        self.fimctrl.generated_plot_needs_update = True
    
    def set_match_threshold(self, threshold:float):
        self.fimctrl.match_threshold = threshold
        self.fimctrl.generated_plot_needs_update = True

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
        self.supports_interpolative_models = True
        self.total_time = 0.0
        self.transition_frame = None
        self.preprocessed_secondary_motion = None
        self.total_secondary_frames = 0
        self.interpolating = False
        self.num_channels = 0
        self.src_len = 5
        self.tgt_len = 5
        self.src_start = 0
        self.tgt_start = 0
        self.generated_plot_needs_update = True
        self.name = "FIM"
        self.match_threshold = np.pi/45
        self.transition_fade_frames = 15
    
    def preprocess_secondary(self):
        if self.model is None:
            print("Model not loaded")
            return
        if self.anim_file_ctrl2.motion is None:
            return
        if self.anim_file_ctrl2.fps != self.anim_file_ctrl.fps:
            if self.anim_file_ctrl.end_time == 0.0:
                self.queue_secondary_loading = True
                return
            print("FPS mismatch between base and secondary animations")
            self.preprocessed_secondary_motion = None
            return
        
        self.total_secondary_frames = self.anim_file_ctrl2.motion.num_frames()
        cached = self._get_cached(SECONDARY_MOTION_CACHE, key2=self.anim_file_ctrl2.filename)
        if cached is not None:
            print("Using cached preprocessed secondary motion")
            self.preprocessed_secondary_motion = cached
        else:
            print("Preprocessing secondary animation")
            
            self.preprocessed_secondary_motion = self.rotations_to_normalized_motion_data(self.anim_file_ctrl2.motion.rotations())
            self._add_cache(self.preprocessed_secondary_motion, SECONDARY_MOTION_CACHE, key2=self.anim_file_ctrl2.filename)
            
    def preprocess_base(self):
        if self.model is None:
            print("Model not loaded")
            return
        if self.anim_file_ctrl.motion is None:
            return
        
        cached = self._get_cached(BASE_MOTION_CACHE)
        if cached is not None:
            print("Using cached preprocessed base motion")
            self.preprocessed_motion = cached
        else:
            print("Preprocessing base animation")
            self.preprocessed_motion = self.rotations_to_normalized_motion_data(self.anim_file_ctrl.motion.rotations())
            self._add_cache(self.preprocessed_motion, BASE_MOTION_CACHE)
        self.computed_poses = self.anim_file_ctrl.motion.poses
        self.total_frames = len(self.computed_poses)
        self.total_time = self.total_frames / self.anim_file_ctrl.fps
        self.transition_frame = None
        self.generated_plot_needs_update = True
        self.num_channels = len(self.anim_file_ctrl.motion.skel.joints)
        self._active_colors_base = np.tile(ACTIVE_COLOR, (self.num_channels,1))
        if self.queue_secondary_loading:
            self.preprocess_secondary()
            self.queue_secondary_loading = False    

    def load_model(self, model_path:str, recompute:bool=False):
        self.generated_plot_needs_update = True
        super().load_model(model_path, recompute)

    def reset_linear_transition(self, linctrl):
        if linctrl.motion is not None:
            linctrl.motion.clear()
            linctrl.digest_motion(self.computed_poses, append=True)

    def generate_linear_transition(self, linctrl, transition_frame):
        if linctrl.motion is None:
            linctrl.create_motion(self.anim_file_ctrl.motion.skel, self.anim_file_ctrl.fps)
        self.lin_transition_frames = 30
        self.lin_src = self.anim_file_ctrl.motion.rotations()
        self.lin_tgt = self.anim_file_ctrl2.motion.rotations()[self.transition_to_frame:]
        lin_res = np.zeros((transition_frame + len(self.lin_tgt) ,*self.lin_src.shape[1:]))
        lin_res[:transition_frame] = self.lin_src[:transition_frame]
        transition_frames = min(self.lin_transition_frames, len(self.lin_tgt), len(self.lin_src) - transition_frame)
        for i in range(transition_frames):
            fade = i / transition_frames
            dst_frame = transition_frame + i
            lin_res[dst_frame] = motion_math.lerp(self.lin_src[dst_frame], self.lin_tgt[i], fade)
        if transition_frames <= self.lin_transition_frames:
            lin_res[transition_frame + transition_frames:] = self.lin_tgt[transition_frames:]
        linctrl.digest_motion(lin_res)
        linctrl.cur_time = transition_frame / self.anim_file_ctrl.fps


    def trigger_transition(self, linctrl):
        if self.preprocessed_secondary_motion is None:
            print("Secondary motion not preprocessed")
            return
        transition_frame = self.anim_file_ctrl.motion.time_to_frame(self.anim_file_ctrl.cur_time)
        self.transition_to_frame = self.anim_file_ctrl2.motion.time_to_frame(self.anim_file_ctrl2.cur_time)

        self.generate_linear_transition(linctrl, transition_frame)
        
        self.match_vector = np.zeros(self.num_channels)
        self.matched_channels = np.full(self.num_channels, True)

        self.computed_poses = self.anim_file_ctrl.motion.poses[:transition_frame]
        self.computed_poses.extend(self.anim_file_ctrl2.motion.poses[self.transition_to_frame:])
        self.target_poses_t = np.array([self.computed_poses[i].data for i in range(len(self.computed_poses))])
        self.target_poses_aa = conversions.R2A(conversions.T2R(self.target_poses_t))
        
        self.total_frames = len(self.computed_poses)
        self.total_time = self.total_frames / self.anim_file_ctrl.fps
        dims = self.preprocessed_motion.shape
        interpolation_buffer = torch.zeros(dims[0], self.total_frames, dims[2], dtype=self.preprocessed_motion.dtype)
        interpolation_buffer[:,:transition_frame] = self.preprocessed_motion[:,:transition_frame]
        interpolation_buffer[:,transition_frame:] = self.preprocessed_secondary_motion[:,self.transition_to_frame:]
        self.interpolation_buffer = interpolation_buffer
        self.interpolation_buffer_untouched = self.interpolation_buffer.clone()
        self.interpolating = True
        self.generated_buffer_for_plot = None
        print("Triggered transition from frame ", transition_frame)
        self.src_start = transition_frame - self.src_len
        self.tgt_start = transition_frame + 1

        self.compute_match_vector(self.target_poses_aa[transition_frame - 1], self.target_poses_aa[transition_frame])

        self.generated_plot_needs_update = True
        self.transition_frame = transition_frame

    def is_ending(self, dt):
        return self.cur_time + dt > self.total_time

    def reset(self):
        super().reset()
        if self.transition_frame is None:
            self.interpolating = False
        if self.interpolating:
            self.src_start = self.transition_frame - self.src_len
            self.tgt_start = self.transition_frame + 1
            self.interpolation_buffer = self.interpolation_buffer_untouched.clone()

    def compute_match_vector(self, src, tgt):
        self.match_vector = np.absolute((tgt - src)).max(1) / np.pi
        self.matched_channels = self.match_vector < self.match_threshold
        self.match_vector[self.matched_channels] = 0.0


    def advance_time(self, dt, params=None):
        if self.computed_poses is not None and len(self.computed_poses):
            try:
                curr_frame = int(self.cur_time * self.anim_file_ctrl.fps + 1e-05)
                self.cur_time += dt
                interpolating = self.transition_frame is not None
                if interpolating != self.interpolating:
                    if not interpolating:
                        print("Performing base animation.")
                    else:
                        print("Performing generated motion.")
                    self.interpolating = interpolating
                if self.cur_time > self.total_time:
                    self.cur_time = 0.0
                    curr_frame = 0
                    if self.interpolating:
                        self.src_start = self.transition_frame - self.src_len
                        self.tgt_start = self.transition_frame + 1
                        self.generated_buffer_for_plot = self.interpolation_buffer[0].clone()
                        if self.generated_plot_needs_update:
                            self.nnutty.plotUpdated.emit(2)
                            self.generated_plot_needs_update = False
                        self.interpolation_buffer = self.interpolation_buffer_untouched.clone()

                if not self.interpolating or curr_frame < self.transition_frame:
                    # copy from base
                    self.settings.color = INACTIVE_COLOR
                    self.pose = self.computed_poses[curr_frame]
                else:
                    # interpolate
                    self.settings.color = self._active_colors_base.copy()
                    self.settings.color[self.matched_channels] = INACTIVE_COLOR
                    src_motion = self.interpolation_buffer[:,self.src_start : self.src_start + self.src_len + self.tgt_len]
                    src_motion = src_motion.reshape(1, int(src_motion.shape[1]/2), src_motion.shape[2]*2)
                    gen_seq = generate.generate(self.model, src_motion, 1, self.device)[:,:,:self.num_dim]


                    fade_in_frame = self.src_start + self.src_len - self.transition_frame + 1
                    available_transition_frames = min(self.transition_fade_frames, self.preprocessed_motion.shape[1] - (self.src_start + self.src_len))
                    if fade_in_frame < available_transition_frames:
                        fade = fade_in_frame / available_transition_frames
                        src_frame = self.preprocessed_motion[0][self.src_start+self.src_len]
                        gen_seq = motion_math.lerp(src_frame, gen_seq, fade)

                    self.interpolation_buffer[0][self.src_start + self.src_len] = gen_seq
                    
                    gen_seq = gen_seq.to(device="cpu").numpy()
                    gen_seq_t, gen_seq_aa = self.normalized_motion_data_to_rotations(gen_seq, return_t_and_aa=True)
                    self.compute_match_vector(gen_seq_aa, self.target_poses_aa[curr_frame])
                    gen_seq_t[self.matched_channels] = self.target_poses_t[curr_frame][self.matched_channels]

                    self.interpolation_buffer[0][self.src_start + self.src_len] = self.rotations_to_normalized_motion_data(conversions.T2R(gen_seq_t)).squeeze()
                    self.pose = Pose(self.anim_file_ctrl.motion.skel, gen_seq_t)
                    self.src_start += 1
                    
            except Exception as e:
                print(f"Error computing pose: {e}")

    def get_plot_data(self, no_cache=False):
        res = self.computed_poses
        if self.transition_frame is not None and self.generated_buffer_for_plot is not None:
            rotations = self.normalized_motion_data_to_rotations(self.generated_buffer_for_plot)
            res = []
            for i in range(len(rotations)):
                res.append(Pose(self.anim_file_ctrl.motion.skel, rotations[i]))
        return get_plot_data_from_poses(self.anim_file_ctrl.motion.skel, res)
    

    