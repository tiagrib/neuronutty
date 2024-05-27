from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings

class DualAnimController(CharacterController):
    def __init__(self, ctrl1:CharacterController, ctrl2:CharacterController,
                 settings:CharacterSettings = None):
        super().__init__(ctrl_type=CharCtrlType.MULTI, settings=settings)
        self.control_count = 2
        self.ctrl1 = ctrl1
        self.ctrl2 = ctrl2
        self.ctrl1.settings.world_offset = [-1.0, 0.0, 0.0]
        self.ctrl2.settings.world_offset = [+1.0, 0.0, 0.0]

    def reset(self):
        self.ctrl1.reset()
        self.ctrl2.reset()

    def advance_time(self, dt, params=None):
        self.ctrl1.advance_time(dt=dt, params=params)
        self.ctrl2.advance_time(dt=dt, params=params)

    def compute(self, dt=None, params=None):
        self.ctrl1.compute(dt=dt, params=params)
        self.ctrl2.compute(dt=dt, params=params)

    def get_pose(self):
        return [self.ctrl1.get_pose(), self.ctrl2.get_pose()]
    
    def get_color(self):
        return [self.ctrl1.settings.color, self.ctrl2.settings.color]
    
    def get_controllers(self):
        return [self.ctrl1, self.ctrl2]