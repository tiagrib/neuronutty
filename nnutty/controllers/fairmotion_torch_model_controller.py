import logging
import os
from pathlib import Path
import torch
import numpy as np
from nnutty.controllers.anim_file_controller import AnimFileController
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings
from nnutty.controllers.uncached_anim_controller import UncachedAnimController
from fairmotion.tasks.motion_prediction import generate, utils
from fairmotion.ops import conversions


class FairmotionModelController(UncachedAnimController):
    def __init__(self, model, settings:CharacterSettings = None):
        super().__init__(ctrl_type=CharCtrlType.MODEL, settings=settings)
        self.orig_anim_length = 0.0
        self.in_prediction = False
        self.anim_file_ctrl = AnimFileController(settings=settings)
        self.load_model(model_path=model)

    def load_model(self, model_path:str):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.num_predictions = 200
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

    def load_anim_file(self, filename:str):
        self.anim_file_ctrl.load_anim_file(filename)
        self.orig_anim_length = self.anim_file_ctrl.end_time
        self.recompute_prediction()

    def recompute_prediction(self):
        logging.info("Running model")
        input_motion = self.anim_file_ctrl.motion.rotations()
        # apply conversions.R2A() to each element of the array's axis 2 using numpy        
        input_motion = conversions.R2A(input_motion[:,:,:])
        input_motion = input_motion.reshape(1, -1, self.num_dim)
        input_motion = torch.from_numpy(input_motion)
        pred_seq = (
            generate.generate(self.model, input_motion, self.num_predictions, self.device)
            .to(device="cpu")
            .numpy()
        )
        self.anim_file_ctrl.digest_motion(pred_seq, append=True)

    def reset(self):
        super().reset()
        self.anim_file_ctrl.reset()

    def advance_time(self, dt, params=None):
        self.anim_file_ctrl.advance_time(dt, params)
        self.cur_time = self.anim_file_ctrl.cur_time
        if self.cur_time > self.orig_anim_length:
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
        self.pose = self.anim_file_ctrl.get_pose()