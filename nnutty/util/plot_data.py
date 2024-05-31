
from thirdparty.fairmotion.ops import conversions

class PlotData:
    def __init__(self, x_values, y_values, labels=None):
        assert(labels is None or (len(labels) == len(y_values)))
        assert(all([len(x_values) == len(yv) for yv in y_values]))
        self.num_frames = len(x_values)
        self.num_plots = len(y_values)
        self.x_values = x_values
        self.y_values = y_values
        self.labels = labels
        

def get_plot_data_from_poses(skel, poses):
        x = list(range(len(poses)))
        frames = []
        labels = []
        labels_ok = False
        for f in x:
            frame_values = []
            for joint_i, joint in enumerate(skel.joints):
                T = poses[f].data[joint_i]
                dofs = joint.info['dof']
                r, p = conversions.T2Rp(T)
                r = conversions.R2A(r)

                if not labels_ok:
                    lbl = joint.name + "."
                    for j in range(dofs):
                        labels.append(lbl + ['rx', 'ry', 'rz', 'px', 'py', 'pz'][j])

                for j in range(dofs):
                    frame_values.append(r[j] if j < 3 else p[j-3])
            labels_ok = True
            frames.append(frame_values)
        y = []
        for j in range(skel.num_dofs):
            y.append([f[j] for f in frames])
        return PlotData(x, y, labels)