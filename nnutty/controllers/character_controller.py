from enum import Enum
from fairmotion.utils import utils

DEFAULT_V_UP = "z"
DEFAULT_V_FRONT = "y"
DEFAULT_SCALE = 1.0

class CharCtrlType(Enum):
    # source of the character is unknown
    UNKNOWN = 0
    # source of the character is from an animation file
    ANIM_FILE = 1
    # source of the character is from a model
    MODEL = 2

class CharacterSettings():
    def __init__(self, v_up=None, v_front=None, scale=None):
        self.v_up = utils.str_to_axis(v_up if v_up else DEFAULT_V_UP)
        self.v_front = utils.str_to_axis(v_front if v_front else DEFAULT_V_FRONT)
        self.scale = scale if scale else DEFAULT_SCALE

class CharacterController():
    def __init__(self, 
                 ctrl_type: CharCtrlType = CharCtrlType.UNKNOWN, 
                 settings:CharacterSettings = None):
        self.ctrl_type = ctrl_type
        if settings is None:
            self.settings = CharacterSettings()
        else:
            self.settings = settings

    def reset(self):
        pass

    def advance_time(self, dt, params={}):
        pass

    def get_pose(self):
        return None
    
    def get_settings(self):
        return CharacterSettings()