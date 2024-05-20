from enum import Enum

from fairmotion.utils import utils
from fairmotion.data import bvh, asfamc

from nnutty.controllers.character_controller import CharCtrlType, CharacterController


class AnimFileType(Enum):
    # source of the character is unknown
    UNKNOWN = 0
    # source of the character is from a bvh file
    BVH = 1
    # source of the character is from an asfamc file
    ASFAMC = 2

class AnimFileController(CharacterController):
    def __init__(self,
                 filename:str,
                 file_type:AnimFileType = AnimFileType.BVH,
                 v_front:str = None,
                 v_up:str = None,
                 scale:float = None,
                 args=None):
        super().__init__(ctrl_type=CharCtrlType.ANIM_FILE)
        if v_up is None:
            v_up = utils.str_to_axis(args.axis_up if args else "y")
        if v_front is None:
            v_front = utils.str_to_axis(args.axis_face if args else "z")
        if scale is None:
            scale = args.scale if args else 1.0

        self.cur_time = 0.0
        self.end_time = 0.0
        self.fps = 1.0
        
        if file_type == AnimFileType.BVH:
            self.motion = bvh.load(
                file=filename,
                v_up_skel=v_up,
                v_face_skel=v_front,
                v_up_env=v_up,
                scale=scale)
        elif file_type == AnimFileType.ASFAMC:
            assert (len(filename) == 2)
            assert(filename[0] is not None and filename[1] is not None)
            self.motion = asfamc.load(file=filename[0], motion=filename[1])
        else:
            self.motion = None

        if self.motion:
            self.end_time = self.motion.length()
            self.fps = self.motion.fps
        
    def reset_pose(self):
        self.cur_time = 0.0

    def advance_time(self, dt, params={}):
        self.cur_time += dt
        if self.cur_time > self.end_time:
            self.reset_pose()

    def get_pose(self):
        if self.motion is None:
            return None
        pose = self.motion.get_pose_by_time(self.cur_time)
        return pose
    

class BVHFileController(AnimFileController):
    def __init__(self,
                 filename:str,
                 v_front:str = None,
                 v_up = None,
                 scale = None,
                 args = None):
        super().__init__(filename=filename,
                         file_type=AnimFileType.BVH,
                         v_front=v_front,
                         v_up=v_up,
                         scale=scale,
                         args=args)


class ASFAMCFileController(AnimFileController):
    def __init__(self,
                 asf_filename:str,
                 asc_filename:str,
                 v_front:str = None,
                 v_up = None,
                 scale = None,
                 args = None):
        super().__init__(filename=[asf_filename, asc_filename],
                         file_type=AnimFileType.ASFAMC,
                         v_front=v_front,
                         v_up=v_up,
                         scale=scale,
                         args=args)