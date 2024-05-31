import logging
import os
from pathlib import Path
import torch
import numpy as np
import matplotlib.pyplot as plt
from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings
from nnutty.controllers.multi_anim_controller import MultiAnimController
from nnutty.controllers.uncached_anim_controller import UncachedAnimController
from thirdparty.fairmotion.tasks.motion_prediction import generate, utils
from thirdparty.fairmotion.core.motion import Pose
from thirdparty.fairmotion.ops import conversions
from nnutty.util.plot_data import PlotData, get_plot_data_from_poses
from nnutty.util import amass_mean_std


class FairmotionDualController(MultiAnimController):
    def __init__(self, model, settings:CharacterSettings = None):
        super().__init__(ctrls=[FairmotionModelController(model, settings=CharacterSettings.copy(settings)),
                                AnimFileController(settings=CharacterSettings.copy(settings))],
                         settings=settings)
        self.ctrl_type = CharCtrlType.DUAL_ANIM_FILE
        self.model_ctrl = self.ctrls[0]
        
    def loads_animations(self):
        return True
        
    def load_model(self, model_path:str):
        self.model_ctrl.load_model(model_path)

    def load_anim_file(self, filename:str, controller_index=0):
        for ctrl in self.ctrls:
            ctrl.load_anim_file(filename)
        self.reset()

    def set_prediction_ratio(self, ratio):
        self.model_ctrl.set_prediction_ratio(ratio)
        self.reset()

    def get_prediction_ratio(self):
        return self.model_ctrl.get_prediction_ratio()
    
    def get_plot_data(self, index):
        return self.ctrls[index].get_plot_data()
    

class FairmotionModelController(UncachedAnimController):
    def __init__(self, model, settings:CharacterSettings = None):
        super().__init__(ctrl_type=CharCtrlType.MODEL, settings=settings)
        self.orig_anim_length = 0.0
        self.in_prediction = False
        self.computed_poses = []
        self.fps = 1.0
        self.prediction_ratio = 0.9
        self.anim_file_ctrl = None
        self.load_model(model_path=model)

    def get_plot_data(self):
        if self.anim_file_ctrl is None or self.anim_file_ctrl.motion is None:
            return None
        
        poses = self.computed_poses

        return get_plot_data_from_poses(self.anim_file_ctrl.motion.skel, poses)

    def load_model(self, model_path:str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.num_dim = 72
        hidden_dim = 1024
        num_layers = 1
        architecture = "seq2seq"
        with open(os.path.join(Path(model_path).parent, "config.txt"), "r") as f:
            config = f.readlines()
            # iterate through each lines and extract the values
            for line in config:
                line = line.strip()
                key = line.split(":")[0]
                value = line[len(key)+1:]
                if key == "hidden_dim":
                    hidden_dim = int(value)
                elif key == "num_layers":
                    num_layers = int(value)
                elif key == "architecture":
                    architecture = value

        logging.info("Preparing model")
        self.model = utils.prepare_model(
            input_dim=self.num_dim,
            hidden_dim=hidden_dim,
            device=self.device,
            num_layers=num_layers,
            architecture=architecture,
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def load_anim_file(self, filename:str, controller_index=0):
        self.anim_file_ctrl = AnimFileController(settings=self.settings)
        self.anim_file_ctrl.load_anim_file(filename)
        self.full_anim_length = self.anim_file_ctrl.end_time
        self.reference_anim_length = self.full_anim_length
        self.fps = self.anim_file_ctrl.fps
        self.recompute_prediction(self.anim_file_ctrl)

    def recompute_prediction(self, anim_file_ctrl):
        if anim_file_ctrl is None or anim_file_ctrl.motion is None:
            return
        
        num_predictions = int(self.prediction_ratio * anim_file_ctrl.motion.num_frames())
        logging.info(f"Running model for {num_predictions} frames...")
        
        self.reference_anim_length = self.full_anim_length - num_predictions/anim_file_ctrl.fps
        self.num_ref_frames = anim_file_ctrl.motion.num_frames() - num_predictions
        input_motion = anim_file_ctrl.motion.rotations()[:self.num_ref_frames]
        input_motion = conversions.R2A(input_motion[:,:,:])
        input_motion = input_motion.reshape(1, -1, self.num_dim)
        input_motion = torch.from_numpy(input_motion)
        pred_seq = (
            generate.generate(self.model, input_motion, num_predictions, self.device)
            .to(device="cpu")
            .numpy()
        )

        self.computed_poses.clear()
        for i in range(self.num_ref_frames):
            self.computed_poses.append(anim_file_ctrl.motion.get_pose_by_frame(i))
        for i in range(num_predictions):
            poses = conversions.A2T(pred_seq[0].reshape(pred_seq[0].shape[0], pred_seq[0].shape[1] // 3, 3))
            self.computed_poses.append(Pose(anim_file_ctrl.motion.skel, poses[i]))
        self.reset()

    def set_prediction_ratio(self, ratio):
        self.prediction_ratio = ratio
        self.recompute_prediction(self.anim_file_ctrl)

    def get_prediction_ratio(self):
        return self.prediction_ratio

    def reset(self):
        super().reset()
        self.cur_time = 0.0

    def advance_time(self, dt, params=None):
        if self.computed_poses:
            self.cur_time += dt
            if self.cur_time > self.full_anim_length:
                self.cur_time = 0.0
            if self.cur_time > self.reference_anim_length:
                if not self.in_prediction:
                    logging.info("Displaying prediction")
                    self.settings.color = np.array([173, 130, 50, 255]) / 255.0  # orange-red
                self.in_prediction = True
            else:
                if self.in_prediction:
                    logging.info("Displaying original animation")
                    self.settings.color = np.array([85, 160, 173, 255]) / 255.0  # blue
                self.in_prediction = False
            self.compute(dt, params)
    
    def compute(self, dt=None, params={}):
        if self.computed_poses:
            pose_i = min(int(self.cur_time * self.fps), len(self.computed_poses) - 1)
            self.pose = self.computed_poses[pose_i]