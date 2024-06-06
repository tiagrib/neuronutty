
import math
import numpy as np
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings
from nnutty.controllers.uncached_anim_controller import UncachedAnimController

from fairmotion.core import motion as motion_classes
from fairmotion.ops import conversions
from fairmotion.utils import constants

def AAx2T(angle):
    return conversions.R2T(conversions.Ax2R(angle))

def CreateLinearSkeleton(joint_names, segment_lengths, last_joint_name=None, settings=None):
    if len(joint_names) == 0 or len(segment_lengths) == 0:
        raise ValueError("joint_names and segment_lengths must have at least one element")
    if len(joint_names) != len(segment_lengths):
        raise ValueError("joint_names and segment_lengths must have the same length")

    if settings:
        skel = motion_classes.Skeleton(v_up=settings.v_up, v_face=settings.v_front, v_up_env=settings.v_up)
    else:
        skel = motion_classes.Skeleton()

    last_joint = None
    for i, joint_name in enumerate(joint_names):
        joint = motion_classes.Joint(name=joint_name)
        offset = np.array([0.0, 0.0, 0.0]) if i == 0 else np.array(segment_lengths[i-1])
        joint.xform_from_parent_joint = conversions.p2T(offset)
        joint.info["type"] = "revolute"
        joint.info["dof"] = 1
        joint.info["bvh_channels"] = ["xrotation"]
        skel.add_joint(joint, last_joint)
        last_joint = joint

    tip_joint = motion_classes.Joint(name="tip" if last_joint_name is None else last_joint_name)
    offset = np.array(segment_lengths[-1])
    tip_joint.xform_from_parent_joint = conversions.p2T(offset)
    skel.add_joint(joint=tip_joint, parent_joint=last_joint)
    
    return skel

def CreateLinearSkelPose(skel, angles):
    pose_data = []
    for i, angle in enumerate(angles):
        T = AAx2T(angle)
        pose_data.append(T)
    pose_data.append(constants.EYE_T)
    return motion_classes.Pose(skel, pose_data)

class WaveAnimController(UncachedAnimController):
    def __init__(self, 
                 nnutty, 
                 channel_name:str = "output",
                 settings:CharacterSettings = None,
                 offset:np.ndarray = np.array([0.0, 10.0, 0.0]),
                 amplitude:float = np.pi,
                 phase:float = 0.0,
                 frequency:float = 1.0,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.WAVE, settings=settings, parent=parent)
        self.output_name = channel_name
        self.output_value = 0.0
        self.amplitude = amplitude
        self.phase = phase
        self.frequency = frequency
        self.skel = CreateLinearSkeleton(["root"], [offset], settings=settings)
        self.pose = CreateLinearSkelPose(self.skel, [0.0])

    def compute(self, dt=None, params={}):
        # update the output_value based on the sinewave of dt
        self.output_value = self.amplitude * (self.phase + math.sin(self.frequency*self.cur_time))
        self.pose.set_transform(0, AAx2T(self.output_value), local=True)
        