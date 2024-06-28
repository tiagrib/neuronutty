from enum import Enum
from fairmotion.utils import utils
from fairmotion.ops import conversions
from PySide6 import QtCore
import numpy as np

DEFAULT_V_UP = "z"
DEFAULT_V_FRONT = "y"
DEFAULT_SCALE = 1.0

class CharCtrlType(Enum):
    UNKNOWN = 0
    ANIM_FILE = 1
    MODEL = 2
    WAVE = 3
    DIP = 4
    MULTI = 5

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
    
    @QtCore.Property(int, constant=True)
    def MULTI(self):
        return CharCtrlType.MULTI.value

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
        self.ground_feet = False
        self.color = np.array([85, 160, 173, 255]) / 255.0  # blue

    @classmethod
    def copy(cls, existing):
        new_settings = cls()
        new_settings.v_up = existing.v_up
        new_settings.v_front = existing.v_front
        new_settings.scale = existing.scale
        new_settings.world_offset = existing.world_offset.copy()
        new_settings.show_origin = existing.show_origin
        new_settings.color = existing.color.copy()
        new_settings.ground_feet = existing.ground_feet
        return new_settings

    def set_world_offset(self, offset):
        self.world_offset = offset

    def set_show_origin(self, show_origin):
        self.show_origin = show_origin

    def set_scale(self, scale):
        self.scale = scale

    def set_ground_feet(self, ground_feet):
        self.ground_feet = ground_feet

class CharacterController():
    def __init__(self, 
                 nnutty,
                 ctrl_type: CharCtrlType = CharCtrlType.UNKNOWN, 
                 settings:CharacterSettings = None,
                 parent=None):
        self.nnutty = nnutty
        self.ctrl_type = ctrl_type
        self.parent = parent
        self.name = "CharCtrl"
        if settings is None:
            self.settings = CharacterSettings()
        else:
            self.settings = settings
        self.feet_pelvis_offset = None

    def loads_animations(self):
        return 0
    
    def loads_folders(self):
        return False
    
    def get_plot_data(self, index=0, no_cache=False):
        return None

    def reset(self):
        pass

    def advance_time(self, dt, params=None):
        pass

    def get_pose(self):
        return None
    
    def get_settings(self):
        return CharacterSettings()
    
    def get_cur_time(self):
        return 0.0
    
    def get_color(self):
        return self.settings.color
    
    def is_ending(self, dt):
        return None
    
    def get_ground_point(self, pose):
        enabled = self.settings.ground_feet
        parent = self.parent
        while not enabled and parent:
            enabled = parent.settings.ground_feet
            parent = parent.parent

        if not enabled:
            return np.array([0.0, 0.0, 0.0])
        
        lfoot_pos = conversions.T2p(pose.get_transform('l_foot', local=False))
        rfoot_pos = conversions.T2p(pose.get_transform('r_foot', local=False))
        foot_diff = rfoot_pos - lfoot_pos

        if foot_diff[1] < 0.01:
            return (lfoot_pos + rfoot_pos) / 2.0
        if lfoot_pos[1] < rfoot_pos[1]:
            return lfoot_pos
        return lfoot_pos
