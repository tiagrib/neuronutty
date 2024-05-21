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
        super().__init__(title="NeuroNutty Viewer",
                         size=(1280, 720),
                         cam=self.cam)
        
    def run(self, **kwargs):
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

    def _render_pose(self, pose, character, color):
        skel = pose.skel
        for j in skel.joints:
            T = pose.get_transform(j, local=False)
            pos = conversions.T2p(T)
            gl_render.render_point(pos, radius=0.03 * self.scale, color=color)
            if j.parent_joint is not None:
                # returns X that X dot vec1 = vec2
                pos_parent = conversions.T2p(
                    pose.get_transform(j.parent_joint, local=False)
                )
                p = 0.5 * (pos_parent + pos) + character.controller.settings.world_offset
                l = np.linalg.norm(pos_parent - pos)
                r = 0.1 * self.thickness
                R = math.R_from_vectors(np.array([0, 0, 1]), pos_parent - pos)
                gl_render.render_capsule(
                    conversions.Rp2T(R, p),
                    l,
                    r * self.scale,
                    color=color,
                    slice=8,
                )

    def _render_characters(self):
        colors = [
            np.array([123, 174, 85, 255]) / 255.0,  # green
            np.array([255, 255, 0, 255]) / 255.0,  # yellow
            np.array([85, 160, 173, 255]) / 255.0,  # blue
        ]
        for i, character in self.nnutty.get_characters():
            
            if character.controller.settings.show_origin:
                gl_render.render_transform(constants.eye_T(), use_arrow=True, line_width=self.nnutty.args.thickness)

            pose = character.get_pose()
            if pose:
                color = colors[i % len(colors)]

                glEnable(GL_LIGHTING)
                glEnable(GL_DEPTH_TEST)

                glEnable(GL_LIGHTING)
                self._render_pose(pose, character, color)

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
                f"Time: {self.cur_time:.2}",
                pos=[0.05 * w, 0.95 * h],
                font=GLUT_BITMAP_TIMES_ROMAN_24,
            )

    def record_callback(self):
        if self.recording:
            image = self.get_screen(render=True)
            self.rec_gif_images.append(
                image.convert("P", palette=Image.ADAPTIVE)
            )
        
        
