import logging
import os
from pathlib import Path
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.tensorboard import SummaryWriter
from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings
from nnutty.controllers.multi_anim_controller import MultiAnimController
from nnutty.controllers.uncached_anim_controller import UncachedAnimController
from fairmotion.tasks.motion_prediction import generate, utils
from fairmotion.core.motion import Pose
from fairmotion.ops import conversions
from nnutty.data.train_config import TrainConfig
from nnutty.tasks.model_mean_std import ModelMeanStd
from nnutty.util.plot_data import PlotData, get_plot_data_from_poses
from nnutty.util import amass_mean_std
from thirdparty.fairmotion.tasks.motion_prediction.dataset import FORCE_DATA_TO_FLOAT32
import time



class FairmotionMultiController(MultiAnimController):
    def __init__(self, nnutty, 
                 model_path:str = None, 
                 settings:CharacterSettings = None,
                 parent=None,
                 animctrl=None,
                 fmctrl=None):
        if animctrl is None:
            animctrl = AnimFileController(nnutty, settings=CharacterSettings.copy(settings), parent=self)
        if fmctrl is None:
            fmctrl = FairmotionModelController(nnutty, model_path, settings=CharacterSettings.copy(settings), animctrl=animctrl, parent=self)
        super().__init__(nnutty,
                         ctrls=[animctrl, fmctrl],
                         settings=settings,
                         parent=parent)
        self.model_ctrls = [self.ctrls[1]]
        
    def loads_animations(self):
        return 1
    
    def loads_folders(self):
        return True
        
    def load_model(self, model_path:str):
        for ctrl in self.model_ctrls:
            ctrl.load_model(model_path, recompute=True)
        self.reset()

    def load_anim_file(self, filename:str, controller_index:int=0, update_plots:bool=False):
        self.model_ctrls[0].load_anim_file(filename)
        for i in range(1, len(self.model_ctrls)):
            self.model_ctrls[i].anim_file_ctrl = self.model_ctrls[0].anim_file_ctrl
        self.reset()
        self.nnutty.plotUpdated.emit(0)

    def set_prediction_ratio(self, ratio):
        for ctrl in self.model_ctrls:
            ctrl.set_prediction_ratio(ratio)
        self.reset()

    def get_prediction_ratio(self):
        return self.model_ctrls[0].get_prediction_ratio()
    
    def get_plot_data(self, index):
        return self.ctrls[index].get_plot_data()
    
    def display_all_models(self, state:bool, selected_item, all_items):
        if state:
            print("Displaying all models in folder", Path(selected_item).parent)
            animctrl = self.ctrls[0]
            self.ctrls = [animctrl]
            self.model_ctrls.clear()
            first_model = True
            for item in all_items:
                modelpath = Path(selected_item).parent / item
                ctrl = FairmotionModelController(self.nnutty, modelpath, settings=CharacterSettings.copy(self.settings), animctrl=animctrl, parent=self, recompute=False)
                if first_model:
                    ctrl.preprocess_motion()
                    first_model = False
                else:
                    ctrl.preprocessed_motion = self.model_ctrls[0].preprocessed_motion
                ctrl.recompute_prediction()
                self.ctrls.append(ctrl)
                self.model_ctrls.append(ctrl)
        else:
            print("Displaying single model: ", Path(selected_item).name)
            animctrl = self.ctrls[0]
            self.ctrls = [animctrl]
            self.model_ctrls = [FairmotionModelController(self.nnutty, selected_item, settings=CharacterSettings.copy(self.settings), animctrl=animctrl, parent=self)]
            self.load_model(selected_item)
            self.model_ctrls[0].preprocess_motion()
            self.model_ctrls[0].recompute_prediction()
        self.reposition_subcontrollers()
    

class FairmotionModelController(UncachedAnimController):
    def __init__(self, nnutty, model_path:str = None, 
                 settings:CharacterSettings = None, 
                 animctrl = None,
                 parent=None,
                 recompute=False):
        super().__init__(nnutty, ctrl_type=CharCtrlType.MODEL, settings=settings, parent=parent)
        self.supports_interpolative_models = False
        self.orig_anim_length = 0.0
        self.in_prediction = False
        self.computed_poses = []
        self.fps = 1.0
        self.representation = "aa"
        self.prediction_ratio = 0.5
        self.anim_file_ctrl = animctrl
        self.preprocessed_motion = None
        self.model_mean = amass_mean_std.AMASS_FULL_MEAN
        self.model_std = amass_mean_std.AMASS_FULL_STD
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_cache = {}
        self.model = None
        self.interpolative = False
        self.model_file_cache = {}
        self.plot_data_cache = {}
        self.current_model_path = None
        self.num_predictions = 0
        if self.anim_file_ctrl is None:
            self.anim_file_ctrl = AnimFileController(settings=self.settings)
        else:
            self.reference_anim_length = self.anim_file_ctrl.end_time
            self.fps = self.anim_file_ctrl.fps
        self.model_name = ""
        if model_path:
            self.load_model(model_path,recompute=recompute)

    def get_plot_data(self):
        if self.anim_file_ctrl is None or self.anim_file_ctrl.motion is None:
            return None
        
        if (self.current_model_path in self.plot_data_cache and 
                self.anim_file_ctrl.filename in self.plot_data_cache[self.current_model_path] and 
                self.num_predictions in self.plot_data_cache[self.current_model_path][self.anim_file_ctrl.filename]):
            return self.plot_data_cache[self.current_model_path][self.anim_file_ctrl.filename][self.num_predictions]
        
        poses = self.computed_poses

        if poses:
            self.plot_data_cache[self.current_model_path][self.anim_file_ctrl.filename][self.num_predictions] = get_plot_data_from_poses(self.anim_file_ctrl.motion.skel, poses)
            return self.plot_data_cache[self.current_model_path][self.anim_file_ctrl.filename][self.num_predictions]
        else:
            return None

    def load_model(self, model_path:str, recompute:bool=False):        
        model_path = Path(model_path)
        if model_path.is_dir():
            model_folder = model_path
            model_path = model_folder / "best.model"
        else:
            model_folder = model_path.parent

        if model_path in self.model_cache:
            self.model = self.model_cache[model_path]
            self.current_model_path = model_path
            logging.info(f"Model loaded into '{self.device}'.")
            if recompute:
                self.preprocess_motion()
                self.recompute_prediction()
            return
        
        config = TrainConfig.from_file(model_folder / "config.txt")
        logging.info(f"Model config: {config}")
        if config.interpolative and not self.supports_interpolative_models:
            print("Interpolative model is not supported by this Controller.")
            return
        if not config.interpolative and self.supports_interpolative_models:
            print("This Controller only supports interpolative models.")
            return

        mean_std = ModelMeanStd(model_folder)
        mean_std.load()
        self.model_mean, self.model_std = mean_std.mean, mean_std.std

        if config.representation != self.representation or config.interpolative != self.interpolative:
            self.preprocessed_motion = None
        
        self.representation = config.representation
        self.interpolative = config.interpolative

        if self.representation == "rotmat":
            # 9 x 24 joints
            self.num_dim = 216
        else:
            # aa, 3 x 24 joints
            self.num_dim = 72

        logging.info(f"Preparing model '{model_path}'...")
        self.model = utils.prepare_model(
            input_dim=self.num_dim * (2 if self.interpolative else 1),
            hidden_dim=config.hidden_dim,
            device=self.device,
            num_layers=config.num_layers,
            num_heads=config.num_heads,
            architecture=config.architecture,
        )
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        self.model_cache[model_path] = self.model
        self.current_model_path = model_path
        logging.info(f"Model loaded into '{self.device}'.")

        self.model_name = model_folder.name

        if recompute:
            self.recompute_prediction()

    def load_anim_file(self, filename:str, controller_index=0):
        if self.model is None:
            print("Model not loaded")
            return
        self.anim_file_ctrl.load_anim_file(filename)
        self.reference_anim_length = self.anim_file_ctrl.end_time
        self.fps = self.anim_file_ctrl.fps
        self.total_frames = self.anim_file_ctrl.motion.num_frames()
        self.preprocess_motion()
        self.recompute_prediction()

    def preprocess_motion(self):
        if self._get_cached(self.num_predictions):
            # if it's already cached then it's already preprocessed
            return
        logging.info("Preprocessing motion...")
        self.preprocessed_motion = self.rotations_to_normalized_motion_data(self.anim_file_ctrl.motion.rotations())

    def rotations_to_normalized_motion_data(self, rotations):
        res = rotations
        if self.representation == "aa":
            res = conversions.R2A(rotations)
        res = res.reshape(1, -1, self.num_dim)
        res[0] = (res[0]-self.model_mean[:self.num_dim]) / (self.model_std[:self.num_dim] + np.finfo(float).eps)
        res = torch.Tensor(res).to(device=self.device)
        if not FORCE_DATA_TO_FLOAT32:
            res = res.double()
        return res

    def normalized_motion_data_to_rotations(self, output):
        output = utils.unnormalize(np.array(output), self.model_mean[:self.num_dim], self.model_std[:self.num_dim])
        output = utils.unflatten_angles(output, self.representation)
        if self.representation == "aa":
            output = conversions.A2R(output)
        output = np.array(output)
        output = conversions.R2T(output)
        return output

    def recompute_prediction(self):
        if self.model is None or self.anim_file_ctrl.motion is None:
            return
        
        self.num_predictions = int(self.prediction_ratio * self.total_frames)
        self.reference_anim_length = self.anim_file_ctrl.end_time - self.num_predictions/self.anim_file_ctrl.fps
        self.num_ref_frames = self.total_frames - self.num_predictions

        cached_predictions = self._get_cached(self.num_predictions)
        if cached_predictions is not None:
            self.computed_poses = cached_predictions
            self.nnutty.plotUpdated.emit(1)
            logging.info(f"Prediction loaded from cache..")
            return
        
        logging.info(f"Running model for {self.num_predictions} frames...")
        
        if self.preprocessed_motion is None:
            self.preprocess_motion()

        input_motion = self.preprocessed_motion[:,:self.num_ref_frames,:]
        writer = SummaryWriter("torchlogs/" + self.model_name + "_" + time.strftime("%Y%m%d-%H%M%S") + "/")
        writer.add_graph(self.model, input_motion)
        writer.close()
        pred_seq = (
            generate.generate(self.model, input_motion, self.num_predictions, self.device)
            .to(device="cpu")
            .numpy()
        )

        computed_motion = self.preprocessed_motion.numpy(force=True)
        computed_motion[:,self.num_ref_frames:] = pred_seq
        computed_motion = self.normalized_motion_data_to_rotations(computed_motion)

        self.computed_poses = []
        for i in range(self.total_frames):
            self.computed_poses.append(Pose(self.anim_file_ctrl.motion.skel, computed_motion[0][i]))
        if self.parent:
            self.parent.reset()
        else:
            self.reset()
        self._cache_computed_poses(self.num_predictions)
        self.nnutty.plotUpdated.emit(1)

    def _get_cached(self, end_key=None, key1=None, key2=None):
        if key1 is None:
            key1 = self.current_model_path
        if key2 is None:
            key2 = self.anim_file_ctrl.filename
        if key1 in self.model_file_cache and key2 in self.model_file_cache[key1]:
            cache = self.model_file_cache[key1][key2]
            if end_key is not None: 
                if end_key in cache:
                    return cache[end_key]
                else:
                    return None
            else:
                return cache
        return None

    def _cache_computed_poses(self, end_index=None):
        self._add_cache(self.computed_poses, end_index)

    def _add_cache(self, data, end_key=None, key1=None, key2=None):
        if key1 is None:
            key1 = self.current_model_path
        if key2 is None:
            key2 = self.anim_file_ctrl.filename
        if key1 not in self.model_file_cache:
            self.model_file_cache[key1] = {}
            self.plot_data_cache[key1] = {}
        if key2 not in self.model_file_cache[key1]:
            self.model_file_cache[key1][key2] = {}
            self.plot_data_cache[key1][key2] = {}
        if end_key is None:
            self.model_file_cache[key1][key2] = data
        else:
            self.model_file_cache[key1][key2][end_key] = data

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
            if self.cur_time > self.anim_file_ctrl.end_time:
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
