# Copyright (c) Facebook, Inc. and its affiliates.

import argparse
import logging
import numpy as np
import os
import pickle

from fairmotion.data import amass_dip
from fairmotion.ops import math, motion as motion_ops
from fairmotion.tasks.motion_prediction import utils
from fairmotion.utils import utils as fairmotion_utils


logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def split_into_windows(motion, window_size, stride):
    """
    Split motion object into list of motions with length window_size with
    the given stride.
    """
    n_windows = (motion.num_frames() - window_size) // stride + 1
    motion_ws = [
        motion_ops.cut(motion, start, start + window_size)
        for start in stride * np.arange(n_windows)
    ]
    return motion_ws


def process_file(ftuple, file_type, create_windows, convert_fn, lengths, transitional=False):
    src_len, tgt_len = lengths
    filepath, file_id = ftuple
    motion = amass_dip.load(filepath, file_type)
    motion.name = file_id

    if create_windows is None and transitional:
        create_windows = (src_len*10, src_len*10)

    if create_windows is not None:
        window_size, window_stride = create_windows
        if motion.num_frames() < window_size:
            return [], []
        matrices = [
            convert_fn(motion_window.rotations()).reshape((motion_window.num_frames(), -1))
            for motion_window in split_into_windows(
                motion, window_size, window_stride
            )
        ]
    else:
        matrices = [convert_fn(motion.rotations()).reshape((motion.num_frames(), -1))]
    
    if transitional:
        src_mtx = []
        tgt_mtx = []
        out_len = tgt_len
        num_windows = len(matrices)
        if (create_windows is not None and
                motion.num_frames()-window_stride*num_windows > src_len + tgt_len): # can add an extra window with the remaining frames
            last_frame = motion.rotations()[window_stride*num_windows:]
            last_frame = convert_fn(last_frame).reshape((last_frame.shape[0], -1))
            matrices.append(last_frame)
        fade = np.square(np.linspace(1, 0, window_size - out_len - tgt_len + 1))
        for m in matrices:
            len_m = len(m)
            for src_start in range(0, len_m - src_len - tgt_len + 1):
                output = m[src_start + src_len:src_start + src_len + out_len, ...]
                const_output = np.repeat(m[src_start + src_len - 1][np.newaxis, :], out_len, 0)
                src_input = m[src_start:src_start + src_len, ...]
                for i in range(len_m - tgt_len - (src_start + src_len) + 1):
                    tgt_start = i + src_start + src_len
                    weight = fade[i]
                    tgt_input = m[tgt_start:tgt_start + tgt_len, ...]
                    src_mtx.append(np.concatenate((src_input, tgt_input),1))
                    tgt_mtx.append(np.concatenate((math.lerp(output, const_output, weight), tgt_input), 1))
                    pass
                
            
    else:
        src_mtx = [matrix[:src_len, ...] for matrix in matrices]
        tgt_mtx = [matrix[src_len : src_len + tgt_len, ...] for matrix in matrices]

    logging.info(f"Processed {file_id}")
    return (src_mtx, tgt_mtx)


def process_split(
    all_fnames, output_path, rep, file_type, src_len, tgt_len, create_windows=None, transitional=False, num_cpus=40
):
    """
    Process data into numpy arrays.

    Args:
        all_fnames: List of filenames that should be processed.
        output_path: Where to store numpy files.
        rep: If the output data should be rotation matrices, quaternions or
            axis angle.
        create_windows: Tuple (size, stride) of windows that should be
            extracted from each sequence or None otherwise.

    Returns:
        Some meta statistics (how many sequences processed etc.).
    """
    assert rep in ["aa", "rotmat", "quat"]
    convert_fn = utils.convert_fn_from_R(rep)
    src_seqs, tgt_seqs = [], []
    if num_cpus == 1:
        for ftuple in all_fnames:
            data = process_file(
                ftuple,
                file_type,
                create_windows,
                convert_fn,
                (src_len, tgt_len),
                transitional,
            )
            src_seqs.extend(data[0])
            tgt_seqs.extend(data[1])
    else:
        data = fairmotion_utils.run_parallel(
            process_file,
            all_fnames,
            num_cpus=num_cpus,
            file_type=file_type,
            create_windows=create_windows,
            convert_fn=convert_fn,
            lengths=(src_len, tgt_len),
            transitional=transitional,
        )
        
        for worker_data in data:
            s, t = worker_data
            src_seqs.extend(s)
            tgt_seqs.extend(t)
    logging.info(f"Processed {len(src_seqs)} sequences")
    pickle.dump((src_seqs, tgt_seqs), open(output_path, "wb"))


def read_content(filepath):
    content = []
    with open(filepath) as f:
        for line in f:
            content.append(line.strip())
    return content

def preprocess(args):
    train_files = read_content(
        os.path.join(args.split_dir, "training_fnames.txt")
    )
    validation_files = read_content(
        os.path.join(args.split_dir, "validation_fnames.txt")
    )
    test_files = read_content(os.path.join(args.split_dir, "test_fnames.txt"))

    train_ftuples = []
    test_ftuples = []
    validation_ftuples = []
    for filepath in fairmotion_utils.files_in_dir(args.input_dir, ext=args.file_type):
        db_name = os.path.split(os.path.dirname(filepath))[1]
        db_name = (
            "_".join(db_name.split("_")[1:])
            if "AMASS" in db_name
            else db_name.split("_")[0]
        )
        f = os.path.basename(filepath)
        file_id = "{}/{}".format(db_name, f)

        if file_id in train_files:
            train_ftuples.append((filepath, file_id))
        elif file_id in validation_files:
            validation_ftuples.append((filepath, file_id))
        elif file_id in test_files:
            test_ftuples.append((filepath, file_id))
        else:
            pass

    output_path = os.path.join(args.output_dir, args.rep)
    if args.transitional:
        output_path = output_path + "_transitional"
    fairmotion_utils.create_dir_if_absent(output_path)

    logging.info("Processing training data...")
    train_dataset = process_split(
        train_ftuples,
        os.path.join(output_path, "train.pkl"),
        rep=args.representation,
        file_type=args.file_type,
        src_len=args.src_len,
        tgt_len=args.tgt_len,
        create_windows=(args.window_size, args.window_stride),
        transitional=args.transitional,
        num_cpus=args.num_cpus
    )

    logging.info("Processing validation data...")
    process_split(
        validation_ftuples,
        os.path.join(output_path, "validation.pkl"),
        rep=args.representation,
        file_type=args.file_type,
        src_len=args.src_len,
        tgt_len=args.tgt_len,
        create_windows=(args.window_size, args.window_stride),
        transitional=args.transitional,
        num_cpus=args.num_cpus
    )

    logging.info("Processing test data...")
    process_split(
        test_ftuples,
        os.path.join(output_path, "test.pkl"),
        rep=args.representation,
        file_type=args.file_type,
        src_len=args.src_len,
        tgt_len=args.tgt_len,
        create_windows=(args.window_size, args.window_stride),
        transitional=args.transitional,
        num_cpus=args.num_cpus
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Location of the downloaded and unpacked zip file. See "
        "https://amass.is.tue.mpg.de/dataset for dataset",
    )
    parser.add_argument(
        "--output-dir", required=True, help="Where to store pickle files."
    )
    parser.add_argument(
        "--split-dir",
        default="./data",
        help="Where the text files defining the data splits are stored.",
    )
    parser.add_argument(
        "--rep",
        type=str,
        help="Angle representation to convert data to",
        choices=["aa", "quat", "rotmat"],
        default="aa",
    )
    parser.add_argument(
        "--src-len",
        type=int,
        default=120,
        help="Number of frames fed as input motion to the model",
    )
    parser.add_argument(
        "--tgt-len",
        type=int,
        default=24,
        help="Number of frames to be predicted by the model",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=180,
        help="Window size for test and validation, in frames.",
    )
    parser.add_argument(
        "--window-stride",
        type=int,
        default=120,
        help="Window stride for test and validation, in frames. This is also"
        " used as training window size",
    )
    parser.add_argument(
        "--file-type",
        type=str,
        help="Dataset file type.",
        choices=["pkl", "npz"],
        default="pkl",
    )
    parser.add_argument(
        "--transitional", 
        action='store_true', 
        help="Use this option to train a transitional model instead of a predictive one",
    )

    args = parser.parse_args()

    preprocess(args)
    