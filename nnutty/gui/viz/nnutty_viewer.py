import math
import os
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from fairmotion.viz import camera, gl_render, glut_viewer
from fairmotion.ops import conversions, math
from fairmotion.utils import utils, constants



from PIL import Image
import numpy as np

from nnutty.controllers.character_controller import CharCtrlType

class NNuttyViewer(glut_viewer.Viewer):
    """
    NNuttyViewer is an extension of the glut_viewer.Viewer class that implements
    requisite callback functions -- render_callback, keyboard_callback,
    idle_callback and overlay_callback.

    """

    def __init__(self, nnutty):
        self.nnutty = nnutty
        self.play_speed = self.nnutty.args.speed
        self.scale = self.nnutty.args.scale
        self.thickness = self.nnutty.args.thickness
        self.render_overlay = self.nnutty.args.render_overlay
        self.hide_origin = self.nnutty.args.hide_origin

        self.recording = False
        self.file_idx = 0
        self.cur_time = 0.0
        self.v_up = utils.str_to_axis(self.nnutty.args.axis_up)
        self.cam = camera.Camera(
            pos=np.array(self.nnutty.args.camera_position),
            origin=np.array(self.nnutty.args.camera_origin),
            vup=self.v_up,
            fov=45.0,
        )
        self.controller_2d_coords = {}
        super().__init__(title="NeuroNutty Viewer",
                         size=(1280, 720),
                         cam=self.cam)

    def run(self, **kwargs):
        import sys
        if 'debugpy' in sys.modules:
            print("Running in VS Code")
            import pydevd;
            pydevd.settrace(suspend=False)
        glut_viewer.Viewer.run(self, **kwargs)

    def destroy(self):
        glutDestroyWindow(self.window)
        sys.exit()

    def keyboard_callback(self, key):
        if key == b"s":
            self.cur_time = 0.0
            self.time_checker.begin()
        elif key == b"+":
            self.play_speed = min(self.play_speed + 0.2, 5.0)
        elif key == b"-":
            self.play_speed = max(self.play_speed - 0.2, 0.2)
        elif (key == b"r" or key == b"v"):
            if self.recording:
                # Stop recording
                self.recording = False
                utils.create_dir_if_absent(os.path.dirname(save_path))
                self.rec_gif_images[0].save(
                    save_path,
                    save_all=True,
                    optimize=False,
                    append_images=self.rec_gif_images[1:],
                    loop=0,
                )
            else:
                # start recording
                self.rec_start_time = self.cur_time
                self.rec_fps = 30
                save_path = input(
                    "Enter directory/file to store screenshots/video: "
                )
                self.rec_screenshots = 0
                self.rec_dt = 1 / self.rec_fps
                self.rec_gif_images = []
                self.recording = True                    
        else:
            return False
        return True

    def _render_pose(self, pose, controller, character, colors):
        skel = pose.skel
        ground_point = controller.get_ground_point(pose)
        #ground_point[0] = 0
        #ground_point[2] = 0
        for i, j in enumerate(skel.joints):
            if isinstance(colors, list) or (isinstance(colors, np.ndarray) and len(colors.shape)>1):
                color = colors[i]
            else:
                color = colors
            T = pose.get_transform(j, local=False)
            pos = conversions.T2p(T)
            pos = pos - ground_point
            pos *=controller.settings.scale
            gl_render.render_point(pos + controller.settings.world_offset, radius=0.03 * self.thickness, color=color)
            if j.parent_joint is not None:
                # returns X that X dot vec1 = vec2
                pos_parent = conversions.T2p(
                    pose.get_transform(j.parent_joint, local=False)
                )
                pos_parent = pos_parent - ground_point
                pos_parent *= controller.settings.scale
                p = 0.5 * (pos_parent + pos) + controller.settings.world_offset
                #p *= controller.settings.scale
                if controller != character.controller:
                    p += character.controller.settings.world_offset

                l = np.linalg.norm(pos_parent - pos)
                r = 0.1 * self.thickness
                R = math.R_from_vectors(np.array([0, 0, 1]), pos_parent - pos)
                gl_render.render_capsule(
                    conversions.Rp2T(R, p),
                    l,
                    r,
                    color=color,
                    slice=8,
                )

    def _render_characters(self):
        default_colors = [
            np.array([123, 174, 85, 255]) / 255.0,  # green
            np.array([255, 255, 0, 255]) / 255.0,  # yellow
            np.array([85, 160, 173, 255]) / 255.0,  # blue
        ]
        self.controller_2d_coords.clear()
        for i, character in self.nnutty.get_characters():
            
            if character.controller.settings.show_origin:
                gl_render.render_transform(conversions.p2T(character.controller.settings.world_offset), 
                                           use_arrow=True, line_width=self.nnutty.args.thickness)

            controllers = character.controller
            ctrl_poses = character.get_pose()
            ctrl_colors = character.get_color()
            if character.controller.ctrl_type in [CharCtrlType.MULTI]:
                controllers = character.controller.get_controllers()
            else:
                ctrl_poses = [ctrl_poses]
                ctrl_colors = [ctrl_colors]
                controllers = [controllers]
            ctrl_colors = [c if c is not None else default_colors[i % len(default_colors)] for i, c in enumerate(ctrl_colors)]

            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)

            num_ctrls = len(controllers)
            for i in range(len(controllers)):
                if ctrl_poses[i] is not None:
                    self.controller_2d_coords[controllers[i]] = gl_render.translateGLToWindowCoordinates(controllers[i].settings.world_offset)
                    self._render_pose(ctrl_poses[i], controllers[i], character, ctrl_colors[i])

    def render_callback(self):
        gl_render.render_ground(
            size=[100, 100],
            color=[0.3, 0.3, 0.3],
            axis=utils.axis_to_str(self.cam_cur.vup),
            origin=not self.hide_origin,
            use_arrow=True,
        )
        self._render_characters()
        self.record_callback()

    def idle_callback(self):
        self.dt = self.time_checker.get_time(restart=False)
        self.cur_time += self.dt
        self.time_checker.begin()

        for i, character in self.nnutty.get_characters():
            character.advance_time(self.dt)

    def overlay_callback(self):
        if self.render_overlay:
            w, h = self.window_size
            gl_render.render_text(
                f"Time: {self.cur_time:.2f}",
                pos=[0.05 * w, 0.95 * h],
                font=GLUT_BITMAP_TIMES_ROMAN_24,
            )

            for i, character in self.nnutty.get_characters():
                ctrl_type = character.controller.ctrl_type

                gl_render.render_text(
                    f"Character #{i}: {ctrl_type.name}; t={character.controller.get_cur_time():.2f}",
                    pos=[0.05 * w, 0.90 * h - 5*i],
                    font=GLUT_BITMAP_TIMES_ROMAN_24,
                )

                controllers = [character.controller]
                if character.controller.ctrl_type in [CharCtrlType.MULTI]:
                    controllers = character.controller.get_controllers()
                
                for ctrl in controllers:
                    if not ctrl in self.controller_2d_coords:
                        continue
                    pos = self.controller_2d_coords[ctrl]
                    pos[1] = 0.15*h
                    gl_render.render_text(
                        f"{ctrl.name}",
                        pos=pos,
                        color=[0.8, 0.6, 0.2, 1.0],
                        font=GLUT_BITMAP_TIMES_ROMAN_24,
                    )

    def record_callback(self):
        if self.recording:
            image = self.get_screen(render=True)
            self.rec_gif_images.append(
                image.convert("P", palette=Image.ADAPTIVE)
            )
