import argparse
from nnutty.viz import nnutty_window

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize BVH file with block body")
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--thickness", type=float, default=1.0,help="Thickness (radius) of character body")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--axis-up", type=str, choices=["x", "y", "z"], default="z")
    parser.add_argument("--axis-face", type=str, choices=["x", "y", "z"], default="y")
    parser.add_argument("--camera-position", nargs="+", type=float, required=False, default=(0.0, 5.0, 5.0))
    parser.add_argument("--camera-origin", nargs="+", type=float, required=False, default=(0, 0.0, 0.0))
    parser.add_argument("--hide-origin", action="store_false")
    parser.add_argument("--render-overlay", action="store_false")
    args = parser.parse_args()

    assert len(args.camera_position) == 3 and len(args.camera_origin) == 3, (
        "Provide x, y and z coordinates for camera position/origin like "
        "--camera-position x y z"
    )
    nnutty_window.main(args)