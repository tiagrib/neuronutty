from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings


class NNController(CharacterController):
    def __init__(self, nnutty, model, 
                 settings:CharacterSettings = None,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.MODEL, settings=settings, parent=parent)
        self.model = model