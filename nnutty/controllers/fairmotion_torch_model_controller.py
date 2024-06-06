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
from fairmotion.tasks.motion_prediction import generate, utils
from fairmotion.core.motion import Pose
from fairmotion.ops import conversions
from nnutty.util.plot_data import PlotData, get_plot_data_from_poses
from nnutty.util import amass_mean_std
from thirdparty.fairmotion.tasks.motion_prediction.dataset import FORCE_DATA_TO_FLOAT32


class FairmotionDualController(MultiAnimController):
    def __init__(self, nnutty, 
                 model_path:str = None, 
                 settings:CharacterSettings = None,
                 parent=None):
        animctrl = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        fmctrl = FairmotionModelController(nnutty, model_path, settings=CharacterSettings.copy(settings), animctrl=animctrl, parent=self)
        super().__init__(nnutty,
                         ctrls=[animctrl, fmctrl],
                         settings=settings,
                         parent=parent)
        self.ctrl_type = CharCtrlType.DUAL_ANIM_FILE
        self.model_ctrl = self.ctrls[1]
        
    def loads_animations(self):
        return True
    
    def loads_folders(self):
        return True
        
    def load_model(self, model_path:str):
        self.model_ctrl.load_model(model_path)

    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        self.model_ctrl.load_anim_file(filename)
        self.reset()
        self.nnutty.plot1Updated.emit()
        self.nnutty.plot2Updated.emit()

    def set_prediction_ratio(self, ratio):
        self.model_ctrl.set_prediction_ratio(ratio)
        self.reset()

    def get_prediction_ratio(self):
        return self.model_ctrl.get_prediction_ratio()
    
    def get_plot_data(self, index):
        return self.ctrls[index].get_plot_data()
    

class FairmotionModelController(UncachedAnimController):
    def __init__(self, nnutty, model_path:str = None, 
                 settings:CharacterSettings = None, 
                 animctrl = None,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.MODEL, settings=settings, parent=parent)
        self.orig_anim_length = 0.0
        self.in_prediction = False
        self.computed_poses = []
        self.fps = 1.0
        self.prediction_ratio = 0.5
        self.anim_file_ctrl = animctrl
        self.preprocessed_motion = None
        self.model_mean = amass_mean_std.AMASS_FULL_MEAN
        self.model_std = amass_mean_std.AMASS_FULL_STD
        if self.anim_file_ctrl is None:
            self.anim_file_ctrl = AnimFileController(settings=self.settings)
            
        if model_path:
            self.load_model(model_path)

    def get_plot_data(self):
        if self.anim_file_ctrl is None or self.anim_file_ctrl.motion is None:
            return None
        
        poses = self.computed_poses

        if poses:
            return get_plot_data_from_poses(self.anim_file_ctrl.motion.skel, poses)
        else:
            return None

    def load_model(self, model_path:str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_path = Path(model_path)
        if model_path.is_dir():
            model_folder = model_path
            model_path = model_folder / "best.model"
        else:
            model_folder = model_path.parent
        self.num_dim = 72
        hidden_dim = 1024
        num_layers = 1
        architecture = "seq2seq"
        with open(Path(model_folder) / "config.txt", "r") as f:
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

        logging.info(f"Preparing model '{model_path}'...")
        self.model = utils.prepare_model(
            input_dim=self.num_dim,
            hidden_dim=hidden_dim,
            device=self.device,
            num_layers=num_layers,
            architecture=architecture,
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        logging.info(f"Model loaded into '{self.device}'.")
        self.recompute_prediction()

    def load_anim_file(self, filename:str, controller_index=0):
        self.anim_file_ctrl.load_anim_file(filename)
        self.full_anim_length = self.anim_file_ctrl.end_time
        self.reference_anim_length = self.full_anim_length
        self.fps = self.anim_file_ctrl.fps
        self.preprocess_motion()
        self.recompute_prediction()

    def preprocess_motion(self):
        self.preprocessed_motion = self.anim_file_ctrl.motion.rotations()
        self.preprocessed_motion = conversions.R2A(self.preprocessed_motion[:,:,:])
        self.preprocessed_motion = self.preprocessed_motion.reshape(1, -1, self.num_dim)
        self.preprocessed_motion[0] = (self.preprocessed_motion[0]-self.model_mean) / (self.model_std + np.finfo(float).eps)
        self.preprocessed_motion = torch.Tensor(self.preprocessed_motion).to(device=self.device)
        if not FORCE_DATA_TO_FLOAT32:
            self.preprocessed_motion = self.preprocessed_motion.double()

    def recompute_prediction(self):
        if self.anim_file_ctrl.motion is None:
            return
        
        num_predictions = int(self.prediction_ratio * self.anim_file_ctrl.motion.num_frames())
        logging.info(f"Running model for {num_predictions} frames...")
        self.reference_anim_length = self.full_anim_length - num_predictions/self.anim_file_ctrl.fps
        self.num_ref_frames = self.anim_file_ctrl.motion.num_frames() - num_predictions

        input_motion = self.preprocessed_motion[:,:self.num_ref_frames,:]
        pred_seq = (
            generate.generate(self.model, input_motion, num_predictions, self.device)
            .to(device="cpu")
            .numpy()
        )
        pred_seq = utils.unnormalize(np.array(pred_seq), self.model_mean, self.model_std)
        pred_seq = utils.unflatten_angles(pred_seq, "aa")
        pred_seq = conversions.A2R(pred_seq)
        #pred_seq = utils.multiprocess_convert(pred_seq, conversions.A2R)
        pred_seq = np.array(pred_seq)
        pred_seq = conversions.R2T(pred_seq)
        self.computed_poses.clear()
        for i in range(self.num_ref_frames):
            self.computed_poses.append(self.anim_file_ctrl.motion.get_pose_by_frame(i))
        for i in range(num_predictions):
            self.computed_poses.append(Pose(self.anim_file_ctrl.motion.skel, pred_seq[0][i]))
        if self.parent:
            self.parent.reset()
        else:
            self.reset()
        self.nnutty.plot1Updated.emit()

    def set_prediction_ratio(self, ratio):
        if ratio != self.prediction_ratio:
            self.prediction_ratio = ratio
            self.recompute_prediction()

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