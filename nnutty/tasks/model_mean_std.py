import logging
import os
from pathlib import Path
import pickle

from nnutty.data.train_config import TrainConfig
from thirdparty.fairmotion.tasks.motion_prediction.dataset import Dataset

DATA_FILENAME = "mean_std.pkl"

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

class ModelMeanStd:
    def __init__(self, path=None, mean=None, std=None):
        self.path = Path(path)
        if self.path.is_file():
            self.path = self.path.parent

        self.mean = mean
        self.std = std
        self.data = {
            "model_name": self.path.stem,
            "mean": mean,
            "std": std
        }

    def compute_all_and_save(self):
        logging.info(f"Computing mean-std for models in {self.path}")
        for path in self.path.rglob("*"):
            if path.is_dir():
                for file in path.rglob("*"):
                    if file.is_file() and file.name == "best.model":
                        self.compute_mean(path)
                        self.dump(data_filename=path / DATA_FILENAME)

    def load(self):
        if not (self.path / DATA_FILENAME).is_file():
            logging.info(f"Mean-Std file not found for '{self.path.stem}'. Computing...")
            self.compute_mean(self.path)
            self.dump()
        else:
            self.data = pickle.load(open(self.path / DATA_FILENAME, "rb"))
            self.mean = self.data["mean"]
            self.std = self.data["std"]
            self.model_name = self.data["model_name"]
            logging.info(f"Loaded mean-std for '{self.path.stem}'.")

    def compute_mean(self, model_path):
        logging.info(f"Computing mean for {model_path}")
        config = TrainConfig.from_file(model_path / "config.txt")
        logging.info(config)

        train_data = os.path.join(Path(config.preprocessed_path) / config.representation, f"train.pkl")
        dataset = Dataset(train_data, config.device)
        mean, std = dataset.mean, dataset.std
        self.data = {
            "model_name": model_path.stem,
            "mean": mean,
            "std": std
        }

    def dump(self, data_filename=None):
        if data_filename is None:
            data_filename = self.path / DATA_FILENAME
        pickle.dump(self.data, open(data_filename, "wb"))
        logging.info(f"Saved mean-std '{data_filename}'.")
        
        