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
        
    def run(self):
        filter_description = ("" if not self.mine_only else f"{platform.node().lower()}.") + f"*{CONFIG_EXTENSION}"
        print(f"Watching {self.watch_path} for model configuration files matching: '{filter_description}'")
        while True:
            found = False
            for path in self.watch_path.rglob("*"):
                if path.is_file():
                    if (not self.mine_only or
                        self.mine_only and path.name.split('.')[0] == platform.node().lower()):
                        if path.suffix == ".done" or path.suffix == ".running":
                            continue
                        found = True
                        self.run_job(path)
            if not found:
                print("No jobs found. Sleeping for 5 seconds...")
            time.sleep(5)

    def run_job(self, path):
        print(f"Running {path} containing configuration:")
        config = TrainConfig.from_file(path)
        os.rename(path, path.with_name(f"{path.stem}.running"))

        from fairmotion.tasks.motion_prediction import training
        training.train(config)

        os.rename(path, path.with_name(f"{path.stem}.done"))
