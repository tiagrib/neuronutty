import logging
import os
from pathlib import Path
import pickle

from nnutty.data.train_config import TrainConfig
from thirdparty.fairmotion.tasks.motion_prediction.dataset import Dataset
from fairmotion.tasks.motion_prediction import utils

DATASET_FILES = ["train.pkl", "validation.pkl", "test.pkl"]
DATASET_REPS = ["rotmat", "aa"]

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

class DatasetInfo:
    def __init__(self, path=None):
        self.path = Path(path)
        if self.path.is_file():
            self.path = self.path.parent

    def run(self):
        logging.info(f"Collecting stats for datasets in {self.path}...")
        for path in self.path.rglob("*"):
            if path.is_dir():
                
                for item in path.rglob("*"):
                    if item.is_dir() and item.name in DATASET_REPS:
                        for subitem in item.rglob("*"):
                            if subitem.is_file() and subitem.name in DATASET_FILES:
                                self.print_stats(item)
                                break
                    

    def print_stats(self, dataset_path):
        dataset, _, _, _, _ = utils.prepare_dataset(
            *[dataset_path / file for file in DATASET_FILES],
            batch_size=32,
            device="cuda",
            shuffle=False,
        )
        s = f"\tDataset '{dataset_path}':"
        print(f"{s}{(55-len(s))*' '}# Sequences: {len(dataset['train'].dataset.src_seqs):>6} training, {len(dataset['validation'].dataset.src_seqs):>6} validation, {len(dataset['test'].dataset.src_seqs):>6} test.")  
