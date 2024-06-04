from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings


class DIPModelController(CharacterController):
    def __init__(self, nnutty, settings:CharacterSettings = None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.DIP, settings=settings)
        self.model = None