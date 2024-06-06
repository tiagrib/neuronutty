
import sys
import argparse
from pathlib import Path
from PySide6 import QtWidgets
import torch

ARCHITECTURE_OPTIONS = [
            "seq2seq",
            "tied_seq2seq",
            "transformer",
            "transformer_encoder",
            "rnn",
            "sttransformer",
        ]

def make_parser():
    parser = argparse.ArgumentParser('NeuroNutty', description='NeuroNutty is a tool for neural motion training based on the Fairmotion framework.')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')
    
    train = subparsers.add_parser('train', help='train a model')
    train.add_argument(
        "--preprocessed-path", type=str, help="Path to folder with pickled " "files", required=True,
    )
    train.add_argument(
        "--batch-size", type=int, help="Batch size for training", default=64
    )
    train.add_argument(
        "--shuffle", action='store_true', help="Use this option to enable shuffling",
    )
    train.add_argument(
        "--hidden-dim", type=int, help="Hidden size of LSTM units in encoder/decoder", default=1024,
    )
    train.add_argument(
        "--num-layers", type=int, help="Number of layers of LSTM/Transformer in encoder/decoder", default=1,
    )
    train.add_argument(
        "--num-heads", type=int, help="Number of multiattention heads of Transformer", default=4,
    )
    train.add_argument(
        "--save-model-path", type=str, help="Path to store saved models", required=True,
    )
    train.add_argument(
        "--save-model-frequency", type=int, help="Frequency (in terms of number of epochs) at which model is saved", default=5,
    )
    train.add_argument(
        "--epochs", type=int, help="Number of training epochs", default=200
    )
    train.add_argument(
        "--device", type=str, help="Training device", default=None, choices=["cpu", "cuda"],
    )
    train.add_argument(
        "--architecture", type=str, help="Seq2Seq archtiecture to be used", default="seq2seq", choices=ARCHITECTURE_OPTIONS,
    )
    train.add_argument(
        "--lr", type=float, help="Learning rate", default=None,
    )
    train.add_argument(
        "--optimizer", type=str, help="Torch optimizer", default="sgd", choices=["adam", "sgd", "noamopt"],
    )

    preprocess = subparsers.add_parser('preprocess', help='preprocess datasets')
    preprocess.add_argument( "--input-dir", required=True,
        help="Location of the downloaded and unpacked zip file. See "
        "https://amass.is.tue.mpg.de/dataset for dataset",
    )
    preprocess.add_argument(
        "--output-dir", required=True, help="Where to store pickle files."
    )
    preprocess.add_argument(
        "--split-dir", default="./data", help="Where the text files defining the data splits are stored.",
    )
    preprocess.add_argument(
        "--rep", type=str, help="Angle representation to convert data to", choices=["aa", "quat", "rotmat"], default="aa",
    )
    preprocess.add_argument(
        "--src-len", type=int, default=120, help="Number of frames fed as input motion to the model",
    )
    preprocess.add_argument(
        "--tgt-len", type=int, default=24, help="Number of frames to be predicted by the model",
    )
    preprocess.add_argument(
        "--window-size", type=int, default=180, help="Window size for test and validation, in frames.",
    )
    preprocess.add_argument(
        "--window-stride", type=int, default=120, help="Window stride for test and validation, in frames. This is also used as training window size",
    )
    preprocess.add_argument(
        "--file-type", type=str, help="Dataset file type.", choices=["pkl", "npz"], default="pkl",
    )

    test = subparsers.add_parser('test', help='test a model')
    test.add_argument(
        "--preprocessed-path", type=str, help="Path to folder with pickled" "files from dataset", required=True,
    )
    test.add_argument(
        "--save-model-path", type=str, help="Path to saved models", required=True,
    )
    test.add_argument(
        "--save-output-path", type=str, help="Path to store predicted motion", default=None,
    )
    test.add_argument(
        "--hidden-dim", type=int, help="Hidden size of LSTM units in encoder/decoder", default=1024,
    )
    test.add_argument(
        "--num-layers", type=int, help="Number of layers of LSTM/Transformer in encoder/decoder", default=1,
    )
    test.add_argument(
        "--max-len", type=int, help="Length of seq to generate", default=None,
    )
    test.add_argument(
        "--batch-size", type=int, help="Batch size for testing", default=64
    )
    test.add_argument(
        "--shuffle", action='store_true', help="Use this option to enable shuffling",
    )
    test.add_argument(
        "--epoch", type=int, help="Model from epoch to test, will test on best model if not specified", default=None,
    )
    test.add_argument(
        "--architecture", type=str, help="Seq2Seq archtiecture to be used", default="seq2seq", choices=ARCHITECTURE_OPTIONS,
    )

    train_daemon = subparsers.add_parser('train_daemon', help='Watch for configs to train models')
    train_daemon.add_argument(
        "--watch-path", type=str, help="Path to watch for model config files",
    )

    if len(sys.argv) > 1:        
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args([])
    return args

if __name__ == "__main__":
    # add thirdparty to sys.path
    sys.path.append(str(Path(__file__).resolve().parent / "thirdparty"))
    torch.set_default_dtype(torch.float32)
    args = make_parser()
    if args.command == 'train':
        from fairmotion.tasks.motion_prediction import training
        training.train(args)
    elif args.command == 'preprocess':
        from fairmotion.tasks.motion_prediction import preprocess
        preprocess.preprocess(args)
    elif args.command == 'test':
        from fairmotion.tasks.motion_prediction import testing
        testing.test(args)
    elif args.command == 'train_daemon':
        from nnutty.trainer.train_daemon import TrainDaemon
        daemon = TrainDaemon(args.watch_path)
        daemon.run()
    else:
        app = QtWidgets.QApplication(sys.argv)
        from nnutty.nnutty import NNutty
        nnutty = NNutty(app)
        nnutty.run()