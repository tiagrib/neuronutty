
import math
import numpy as np
from nnutty.controllers.character_controller import CharCtrlType, CharacterSettings
from nnutty.controllers.uncached_anim_controller import UncachedAnimController

from fairmotion.core import motion as motion_classes
from fairmotion.ops import conversions, math as fm_math
from fairmotion.utils import constants

def AAx2T(angle):
    return conversions.R2T(conversions.Ax2R(angle))

class WaveAnimController(UncachedAnimController):
    def __init__(self, 
                 nnutty,
                 settings:CharacterSettings = None,
                 offset:np.ndarray = np.array([0.0, 5.0, 0.0]),
                 amplitude:float = np.pi,
                 phase:float = 0.0,
                 frequency:float = 1.0,
                 parent=None):
        super().__init__(nnutty, ctrl_type=CharCtrlType.WAVE, settings=settings, parent=parent)
        self.segment_offset = offset
        self.num_joints = 0
        self.global_frequency_min = 0.5
        self.global_frequency_max = 1.5
        self.global_range_min = -90
        self.global_range_max = 90
        self.rot_axes = None
        self.clear_skeleton()

    def CreateLinearSkeleton(self, rot_axes=None, last_joint_name=None):
        if len(self.joints) == 0 or len(self.segment_offset) == 0:
            raise ValueError("joint_names and segment_offsets must have at least one element")
        if isinstance(self.segment_offset, list) and isinstance(self.segment_offset[0], float):
            self.segment_offset = [self.segment_offset]*len(self.joints)
        elif isinstance(self.segment_offset, np.ndarray) and len(self.segment_offset.shape) == 1:
            self.segment_offset = [self.segment_offset]*len(self.joints)
        if len(self.joints) != len(self.segment_offset):
            self.segment_offset.extend((len(self.joints)-len(self.segment_offset))*[self.segment_offset[-1]])

        if rot_axes is None:
            rot_axes = [np.array([1.0, 0.0, 0.0])]*len(self.joints)
        if self.rot_axes is None:
            self.rot_axes = rot_axes

        if self.settings:
            skel = motion_classes.Skeleton(v_up=self.settings.v_up, v_face=self.settings.v_front, v_up_env=self.settings.v_up)
        else:
            skel = motion_classes.Skeleton()

        last_joint = None
        for i, joint_name in enumerate(self.joints):
            joint = motion_classes.Joint(name=joint_name)
            offset = np.array([0.0, 0.0, 0.0]) if i == 0 else np.array(self.segment_offset[i-1])
            joint.xform_from_parent_joint = conversions.p2T(offset)
            joint.info["type"] = "revolute"
            joint.info["dof"] = 1
            joint.info["bvh_channels"] = ["xrotation"]
            skel.add_joint(joint, last_joint)
            last_joint = joint

        tip_joint = motion_classes.Joint(name="tip" if last_joint_name is None else last_joint_name)
        offset = np.array(self.segment_offset[-1])
        tip_joint.xform_from_parent_joint = conversions.p2T(offset)
        skel.add_joint(joint=tip_joint, parent_joint=last_joint)
        
        return skel

    def CreateLinearSkelPose(self, angles=None):
        if angles is None:
            angles = [0.0] * len(self.joints)
        pose_data = []
        for i, angle in enumerate(angles):
            T = AAx2T(angle)
            pose_data.append(T)
        pose_data.append(constants.EYE_T)
        return motion_classes.Pose(self.skel, pose_data)

    def clear_skeleton(self):
        self.joints = []
        self.range_min = []
        self.range_max = []
        self.phase = []
        self.frequency = []
        self.output_value = []
        self.rot_axes = []
        self.skel = None
        self.pose = None

    def add_joint(self, name=None, min_range=-np.pi, max_range=np.pi, frequency=None, phase=None):
        if name is None:
            name = "joint" + str(len(self.joints))
        if phase is None:
            phase = np.random.uniform(-np.pi, np.pi)
        if frequency is None:
            frequency = np.random.uniform(self.global_frequency_min, self.global_frequency_max)
        if min_range is None:
            min_range = np.random.uniform(self.global_range_min, self.global_range_max)
        if max_range is None:
            max_range = np.random.uniform(self.global_range_min, self.global_range_max)
        if min_range > max_range:
            min_range, max_range = max_range, min_range
        self.joints.append(name)
        self.range_min.append(min_range)
        self.range_max.append(max_range)
        self.phase.append(phase)
        self.frequency.append(frequency)
        self.output_value.append((max_range+min_range)/2.0)
        self.rot_axes.append(np.array([1.0, 0.0, 0.0]))
        self.rebuild_skeleton()

    def randomize_joints(self):
        range_min = []
        range_max = []
        phase = []
        frequency = []
        rot_axes = []
        for i in range(self.num_joints):
            range_decay = (i+1)/self.num_joints
            r1, r2 = np.random.uniform(self.global_range_min, self.global_range_max, 2)
            range_min.append(min(r1, r2)*range_decay)
            range_max.append(max(r1, r2)*range_decay)
            phase.append(np.random.uniform(-np.pi, np.pi))
            frequency.append(np.random.uniform(self.global_frequency_min, self.global_frequency_max))
            rot_axes.append(np.array([np.random.uniform(-1.0,1.0), np.random.uniform(-1.0,1.0), np.random.uniform(-1.0,1.0)]))
            rot_axes[-1] = fm_math.normalize(rot_axes[-1])
        self.range_min = range_min
        self.range_max = range_max
        self.phase = phase
        self.frequency = frequency
        self.rot_axes = rot_axes
        self.rebuild_skeleton()

    def rebuild_skeleton(self):
        self.skel = self.CreateLinearSkeleton()
        self.pose = self.CreateLinearSkelPose()
        self.num_joints = len(self.joints)
        
    def compute(self, dt=None, params={}):
        # update the output_values based on the sinewave of dt
        for i in range(self.num_joints):
            joint_range = self.range_max[i] - self.range_min[i]
            output_value = self.range_min[i] + joint_range * (1+math.sin(self.phase[i] + self.frequency[i] * self.cur_time))/2
            outputT = conversions.A2T(self.rot_axes[i] * np.deg2rad(output_value))
            self.pose.set_transform(i, outputT, local=True)
            self.output_value[i] = output_value

    def set_min_range(self, x):
        self.global_range_min = x

    def set_max_range(self, x):
        self.global_range_max = x

    def set_min_frequency(self, x):
        self.global_frequency_min = x

    def set_max_frequency(self, x):
        self.global_frequency_max = x