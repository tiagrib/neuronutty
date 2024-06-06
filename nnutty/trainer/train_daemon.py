from pathlib import Path
import platform
import time
import os
from nnutty.data.train_config import TrainConfig

CONFIG_EXTENSION = ".config"

class TrainDaemon:
    def __init__(self, watch_path:str=None, mine_only:bool=True):
        self.mine_only = mine_only
        if watch_path is None:
            watch_path = Path(__file__).resolve().parent
        else:
            watch_path = Path(watch_path)
        self.watch_path = watch_path

    def is_valid(self, file_path, running=False, override_mine_only=None):
        mine_only = self.mine_only
        if override_mine_only is not None:
            mine_only = override_mine_only
        if (file_path.is_file() and 
            (not mine_only or
             (self.mine_only and (
                 (file_path.name.split('.')[0] == platform.node().lower()) or
                 (len(file_path.name.split('.')) < 3)))) and
             ((not file_path.suffix == ".done") or
              (running and not file_path.suffix == ".running"))):
              return True
        return False
            
        
    def run(self):
        filter_description = ("" if not self.mine_only else f"{platform.node().lower()}.") + f"*{CONFIG_EXTENSION}"
        print(f"Watching {self.watch_path} for model configuration files matching: '{filter_description}'")

        for path in self.watch_path.rglob("*"):
            if self.is_valid(path, running=True, override_mine_only=True):
                print(f"Reset '{path}'.")
                os.rename(path, path.with_name(f"{path.stem}.txt"))

        while True:
            found = False
            for path in self.watch_path.rglob("*"):
                if self.is_valid(path):
                    self.run_job(path)
            if not found:
                print("No jobs found. Sleeping for 5 seconds...")
            time.sleep(5)

    def run_job(self, path):
        config = TrainConfig.from_file(path)
        dataset_name = Path(config.preprocessed_path).parent.stem
        model_name = f"{dataset_name}_{config.architecture}_{config.hidden_dim}hd_{config.num_layers}l"
        if "transformer" in config.architecture:
            model_name += f"_{config.num_heads}heads"
        config.save_model_path = str(Path(config.save_model_path) / model_name)
        
        print(f"Running {path} containing configuration:")
        print(config)
        job_name = path.stem
        if job_name.split('.')[0] != platform.node().lower():
            job_name = f"{platform.node().lower()}.{job_name}"
        job_name = f"{job_name}.running"
        new_path = path.with_name(job_name)
        os.rename(path, new_path)
        path = new_path

        from fairmotion.tasks.motion_prediction import training
        training.train(config)

        os.rename(path, path.with_name(f"{path.stem}.done"))
