from nnutty.controllers.character_controller import CharCtrlType, CharacterController, CharacterSettings
from fairmotion.core.motion import Motion
from fairmotion.ops import conversions
from nnutty.util.plot_data import get_plot_data_from_poses

class CachedAnimController(CharacterController):
    def __init__(self, 
                 nnutty, 
                 ctrl_type:CharCtrlType = CharCtrlType.UNKNOWN,
                 settings:CharacterSettings = None,
                 parent=None):
        super().__init__(nnutty, ctrl_type=ctrl_type, settings=settings, parent=parent)
        self.cur_time = 0.0
        self.end_time = 0.0
        self.fps = 1.0
        self.motion = None

    def loads_animations(self):
        return 1

    def digest_fairmotion(self, motion):
        self.digest_motion(motion)

    def create_motion(self, skel, fps):
        self.motion = Motion(skel=skel, fps=fps)

    def digest_motion(self, motion, append=False, skel=None, fps=None):
        if not append and isinstance(motion, Motion):
            self.motion = motion
        else:
            if isinstance(motion, Motion):
                if self.motion is None:
                    self.motion = motion
                else:
                    for i in range(motion.num_frames()):
                        self.motion.add_one_frame(motion.get_pose_by_frame(i))
            else:
                assert(not(self.motion is None) and (skel is None or fps is not None))
                if self.motion is None:
                    self.motion = Motion(skel=self.motion.skel, fps=self.motion.fps)
                else:
                    self.motion.clear()
                    
                # shape is (num_frames, num_inputs = 3 * num_joints)
                if motion.shape[-1] != 3 and motion.shape[-2] != 3:
                    frames = motion.reshape(motion[0].shape[0], 24, 3)
                    frames = conversions.A2T(frames)
                else:
                    frames = conversions.R2T(motion)
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

    def is_ending(self, dt):
        return self.cur_time + dt > self.end_time

    def get_pose(self):
        if self.motion is None or self.motion.num_frames() == 0:
            return None
        pose = self.motion.get_pose_by_time(self.cur_time)
        return pose
    
    def get_cur_time(self):
        return self.cur_time

    def get_plot_data(self, index=0, no_cache=False):
        if self.motion is None:
            return None
        
        poses = [self.motion.get_pose_by_frame(f) for f in range(self.motion.num_frames())]
        return get_plot_data_from_poses(self.motion.skel, poses)

    