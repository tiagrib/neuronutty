from nnutty.controllers.character_controller import CharCtrlType, CharacterController


class NNController(CharacterController):
    def __init__(self, model, args):
        super().__init__(ctrl_type=CharCtrlType.MODEL)
        self.model = model