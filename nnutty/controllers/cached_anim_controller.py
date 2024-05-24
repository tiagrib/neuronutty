from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings

class CachedAnimController(CharacterController):
    def __init__(self, 
                 ctrl_type:CharCtrlType = CharCtrlType.UNKNOWN,
                 settings:CharacterSettings = None):
        super().__init__(ctrl_type=ctrl_type, settings=settings)
        self.cur_time = 0.0
        self.end_time = 0.0
        self.fps = 1.0
        self.motion = None

    def digest_fairmotion(self, motion):
        self.digest_motion(motion)

    def digest_motion(self, motion):
        self.motion = motion
        self.end_time = self.motion.length()
        self.fps = self.motion.fps
        self.reset()

    def reset(self):
        self.cur_time = 0.0

    def advance_time(self, dt, params=None):
        self.cur_time += dt
        if self.cur_time > self.end_time:
            self.reset()

    def get_pose(self):
        if self.motion is None:
            return None
        pose = self.motion.get_pose_by_time(self.cur_time)
        return pose