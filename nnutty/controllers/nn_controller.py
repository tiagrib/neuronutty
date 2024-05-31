from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings


class NNController(CharacterController):
    def __init__(self, model, settings:CharacterSettings = None):
        super().__init__(ctrl_type=CharCtrlType.MODEL, settings=settings)
        self.model = model