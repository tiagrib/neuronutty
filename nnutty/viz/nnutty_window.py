from threading import Lock
import math
import os

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from fairmotion.viz import camera, gl_render, glut_viewer
from fairmotion.ops import conversions
from fairmotion.utils import utils

from PIL import Image
import numpy as np


class NNuttyViewer(glut_viewer.Viewer):
    """
    NNuttyViewer is an extension of the glut_viewer.Viewer class that implements
    requisite callback functions -- render_callback, keyboard_callback,
    idle_callback and overlay_callback.

    """

    def __init__(
        self,
        play_speed=1.0,
        scale=1.0,
        thickness=1.0,
        render_overlay=False,
        hide_origin=False,
        **kwargs,
    ):
        self.characters = []
        self.recording = False
        self.play_speed = play_speed
        self.render_overlay = render_overlay
        self.hide_origin = hide_origin
        self.file_idx = 0
        self.cur_time = 0.0
        self.scale = scale
        self.thickness = thickness
        self.mutex_characters = Lock()
        super().__init__(**kwargs)

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

    def _render_pose(self, pose, body_model, color):
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
                p = 0.5 * (pos_parent + pos)
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

    def _render_characters(self, colors):
        char_enum = None
        with self.mutex_characters:
            char_enum = enumerate(self.characters)

        for i, character in char_enum:
            pose = character.get_pose()
            color = colors[i % len(colors)]

            glEnable(GL_LIGHTING)
            glEnable(GL_DEPTH_TEST)

            glEnable(GL_LIGHTING)
            self._render_pose(pose, character.body_model.name, color)

    def render_callback(self):
        gl_render.render_ground(
            size=[100, 100],
            color=[0.3, 0.3, 0.3],
            axis=utils.axis_to_str(self.cam_cur.vup),
            origin=not self.hide_origin,
            use_arrow=True,
        )
        colors = [
            np.array([123, 174, 85, 255]) / 255.0,  # green
            np.array([255, 255, 0, 255]) / 255.0,  # yellow
            np.array([85, 160, 173, 255]) / 255.0,  # blue
        ]
        self._render_characters(colors)
        self.record_callback()

    def idle_callback(self):
        time_elapsed = self.time_checker.get_time(restart=False)
        self.cur_time += self.play_speed * time_elapsed
        self.time_checker.begin()

    def overlay_callback(self):
        if self.render_overlay:
            w, h = self.window_size
            t = self.cur_time
            frame = 0
            gl_render.render_text(
                f"Frame number: {frame}",
                pos=[0.05 * w, 0.95 * h],
                font=GLUT_BITMAP_TIMES_ROMAN_24,
            )

    def record_callback(self):
        if self.recording:
            image = self.get_screen(render=True)
            self.rec_gif_images.append(
                image.convert("P", palette=Image.ADAPTIVE)
            )

def main(args):
    v_up_env = utils.str_to_axis(args.axis_up)

    cam = camera.Camera(
        pos=np.array(args.camera_position),
        origin=np.array(args.camera_origin),
        vup=v_up_env,
        fov=45.0,
    )
    viewer = NNuttyViewer(
        play_speed=args.speed,
        scale=args.scale,
        thickness=args.thickness,
        render_overlay=args.render_overlay or True,
        hide_origin=args.hide_origin,
        title="NeuroNutty Viewer",
        cam=cam,
        size=(1280, 720),
    )
    viewer.run()
