

from nnutty.controllers.character_controller import CharacterSettings
from nnutty.controllers.fairmotion_torch_model_controller import FairmotionMultiController


class FairmotionInterpolativeController(FairmotionMultiController):
    def __init__(self, nnutty, 
                 model_path:str = None, 
                 settings:CharacterSettings = None,
                 parent=None):
        super(FairmotionInterpolativeController, self).__init__(nnutty, 
                                                                model_path=model_path, 
                                                                settings=settings, 
                                                                parent=parent)