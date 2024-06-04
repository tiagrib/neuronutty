from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings

class UncachedAnimController(CharacterController):
    def __init__(self, 
                 nnutty, 
                 ctrl_type:CharCtrlType = CharCtrlType.UNKNOWN,
                 settings:CharacterSettings = None):
        super().__init__(nnutty, ctrl_type=ctrl_type, settings=settings)
        self.cur_time = 0.0
        self.end_time = 0.0
        self.fps = 1.0
        self.pose = None

    def reset(self):
        self.cur_time = 0.0

    def advance_time(self, dt, params=None):
        self.cur_time += dt
        self.compute(dt, params)

    def compute(self, dt=None, params=None):
        pass

    def get_pose(self):
        return self.pose
    
    def get_cur_time(self):
        return self.cur_time