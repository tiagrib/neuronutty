from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings
from fairmotion.core.motion import Motion
from fairmotion.ops import conversions

class CachedAnimController(CharacterController):
    def __init__(self, 
                 ctrl_type:CharCtrlType = CharCtrlType.UNKNOWN,
                 settings:CharacterSettings = None):
        super().__init__(ctrl_type=ctrl_type, settings=settings)
        self.cur_time = 0.0
        self.end_time = 0.0
        self.fps = 1.0
        self.motion = None

    def loads_animations(self):
        return True

    def digest_fairmotion(self, motion):
        self.digest_motion(motion)

    def digest_motion(self, motion, append=False):
        if not append:
            self.motion = motion
        else:
            if isinstance(motion, Motion):
                for i in range(motion.num_frames()):
                    self.motion.add_one_frame(motion.get_pose_by_frame(i))
            else:
                # shape is (1, num_frames, num_inputs = 3 * num_joints)
                frames = motion[0].reshape(motion[0].shape[0], 24, 3)
                frames = conversions.A2T(frames)
                for i in range(len(frames)):
                    self.motion.add_one_frame(frames[i])
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