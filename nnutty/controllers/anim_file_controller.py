from enum import Enum

from fairmotion.data import bvh, asfamc

from nnutty.controllers.cached_anim_controller import CachedAnimController
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings


class AnimFileType(Enum):
    # source of the character is unknown
    UNKNOWN = 0
    # source of the character is from a bvh file
    BVH = 1
    # source of the character is from an asfamc file
    ASFAMC = 2

class AnimFileController(CachedAnimController):
    def __init__(self,
                 filename:str,
                 file_type:AnimFileType = AnimFileType.BVH,
                 settings:CharacterSettings = None):
        super().__init__(ctrl_type=CharCtrlType.ANIM_FILE, settings=settings)
        
        motion = None
        if file_type == AnimFileType.BVH:
            motion = bvh.load(
                file=filename,
                v_up_skel=self.settings.v_up,
                v_face_skel=self.settings.v_front,
                v_up_env=self.settings.v_up,
                scale=self.settings.scale)
        elif file_type == AnimFileType.ASFAMC:
            assert (len(filename) == 2)
            assert(filename[0] is not None and filename[1] is not None)
            motion = asfamc.load(file=filename[0], motion=filename[1])

        if motion:
            self.digest_fairmotion(motion)

class BVHFileController(AnimFileController):
    def __init__(self,
                 filename:str,
                 v_front:str = None,
                 v_up:str = None,
                 scale:str = None):
        super().__init__(filename=filename,
                         file_type=AnimFileType.BVH,
                         settings=CharacterSettings(v_front=v_front, v_up=v_up, scale=scale))


class ASFAMCFileController(AnimFileController):
    def __init__(self,
                 asf_filename:str,
                 asc_filename:str,
                 v_front:str = None,
                 v_up:str = None,
                 scale:str = None):
        super().__init__(filename=[asf_filename, asc_filename],
                         file_type=AnimFileType.ASFAMC,
                         settings=CharacterSettings(v_front=v_front, v_up=v_up, scale=scale))