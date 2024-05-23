from enum import Enum
from fairmotion.utils import utils
from PySide6 import QtCore

DEFAULT_V_UP = "z"
DEFAULT_V_FRONT = "y"
DEFAULT_SCALE = 1.0

class CharCtrlType(Enum):
    UNKNOWN = 0
    ANIM_FILE = 1
    MODEL = 2
    WAVE = 3
    DIP = 4

    def __str__(self):
        return self.name

class CharCtrlTypeWrapper(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

    @QtCore.Property(int, constant=True)
    def UNKNOWN(self):
        return CharCtrlType.UNKNOWN.value

    @QtCore.Property(int, constant=True)
    def ANIM_FILE(self):
        return CharCtrlType.ANIM_FILE.value

    @QtCore.Property(int, constant=True)
    def MODEL(self):
        return CharCtrlType.MODEL.value

    @QtCore.Property(int, constant=True)
    def WAVE(self):
        return CharCtrlType.WAVE.value
    
    @QtCore.Property(int, constant=True)
    def DIP(self):
        return CharCtrlType.DIP.value

class CharacterSettings():
    def __init__(self, v_up=None, v_front=None, scale=None, args=None):
        if args:
            v_up = args.axis_up
            v_front = args.axis_face
            scale = args.scale

        self.v_up = utils.str_to_axis(v_up if v_up else DEFAULT_V_UP)
        self.v_front = utils.str_to_axis(v_front if v_front else DEFAULT_V_FRONT)
        self.scale = scale if scale else DEFAULT_SCALE
        self.world_offset = [0.0, 0.0, 0.0]
        self.show_origin = True

    def set_world_offset(self, offset):
        self.world_offset = offset

    def set_show_origin(self, show_origin):
        self.show_origin = show_origin

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

    def advance_time(self, dt, params=None):
        pass

    def get_pose(self):
        return None
    
    def get_settings(self):
        return CharacterSettings()