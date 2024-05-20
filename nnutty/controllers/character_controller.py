from enum import Enum

class CharCtrlType(Enum):
    # source of the character is unknown
    UNKNOWN = 0
    # source of the character is from an animation file
    ANIM_FILE = 1
    # source of the character is from a model
    MODEL = 2


class CharacterController():
    def __init__(self, ctrl_type: CharCtrlType = CharCtrlType.UNKNOWN):
        self.ctrl_type = ctrl_type