# Copyright (c) Facebook, Inc. and its affiliates.

import argparse
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import os
import random
import torch
import torch.nn as nn
import sys
import time

from nnutty.data.train_config import TrainConfig
from nnutty.tasks.model_mean_std import ModelMeanStd
from nnutty.util import pretty_time_delta

sys.path.append(r"C:/repo/neuronutty/thirdparty")

from fairmotion.tasks.motion_prediction import generate, utils, test
from fairmotion.utils import utils as fairmotion_utils
from fairmotion.tasks.motion_prediction.dataset import FORCE_DATA_TO_FLOAT32


logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def set_seeds():
    torch.manual_seed(1)
    np.random.seed(1)
    random.seed(1)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train(args):
    logging.info(str(args))
    fairmotion_utils.create_dir_if_absent(args.save_model_path)
    dataset_name = Path(args.preprocessed_path).stem
    dataset_path = TrainConfig.get_preprocessed_path(args)
    
    if args.interpolative:
        model_name = f"{dataset_name}_{args.representation}_tran_{args.architecture}_{args.hidden_dim}hd_{args.num_layers}l"
    else:
        model_name = f"{dataset_name}_{args.representation}_{args.architecture}_{args.hidden_dim}hd_{args.num_layers}l"
    if "transformer" in args.architecture:
        model_name += f"_{args.num_heads}heads"
    dest_model_path = str(Path(args.save_model_path) / model_name)
    
    fairmotion_utils.create_dir_if_absent(dest_model_path)
    utils.log_config(dest_model_path, args)
    args.save_model_path = dest_model_path
    
    set_seeds()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device = args.device if args.device else device
    logging.info(f"Using device: {device}")

    logging.info("Preparing dataset...")
    dataset, mean, std = utils.prepare_dataset(
        *[
            str(dataset_path / f"{split}.pkl")
            for split in ["train", "test", "validation"]
        ],
        batch_size=args.batch_size,
        device=device,
        shuffle=args.shuffle,
    )

    mean_std = ModelMeanStd(args.save_model_path, mean=mean, std=std)
    mean_std.dump()

    # Loss per epoch is the average loss per sequence
    num_training_sequences = len(dataset["train"]) * args.batch_size

    # number of predictions per time step = num_joints * angle representation
    # shape is (batch_size, seq_len, num_predictions)
    _, tgt_len, num_predictions = next(iter(dataset["train"]))[1].shape
    input_dim = num_predictions

    model = utils.prepare_model(
        input_dim=input_dim,
        hidden_dim=args.hidden_dim,
        device=device,
        num_layers=args.num_layers,
        architecture=args.architecture,
        output_dim=num_predictions
    )

    criterion = nn.MSELoss()
    model.init_weights()
    training_losses, val_losses = [], []
    
    logging.info("Preevaluating model...")
    epoch_loss = 0
    start_time = time.perf_counter()
    for iterations, (src_seqs, tgt_seqs) in enumerate(dataset["train"]):
        model.eval()
        src_seqs, tgt_seqs = src_seqs.to(device), tgt_seqs.to(device)
        outputs = model(src_seqs, tgt_seqs, teacher_forcing_ratio=1,)
        loss = criterion(outputs, tgt_seqs)
        epoch_loss += loss.item()
    epoch_time = time.perf_counter() - start_time
    print(f"Epoch time: {epoch_time:.2f} seconds. {pretty_time_delta(args.epochs*epoch_time)} estimated for full training.")
    epoch_loss = epoch_loss / num_training_sequences
    val_loss = generate.eval(
        model, criterion, dataset["validation"], args.batch_size, device,
    )
    logging.info(
        "Before training: "
        f"Training loss {epoch_loss} | "
        f"Validation loss {val_loss}"
    )

    logging.info("Training model...")
    torch.autograd.set_detect_anomaly(True)
    opt = utils.prepare_optimizer(model, args.optimizer, args.lr)
    start_time = time.perf_counter()
    for epoch in range(args.epochs):
        epoch_loss = 0
        model.train()
        teacher_forcing_ratio = np.clip(
            (1 - 2 * epoch / args.epochs), a_min=0, a_max=1,
        )
        logging.info(
            f"Running epoch {epoch} | "
            f"teacher_forcing_ratio={teacher_forcing_ratio}"
        )
        for iterations, (src_seqs, tgt_seqs) in enumerate(dataset["train"]):
            opt.optimizer.zero_grad()
            src_seqs, tgt_seqs = src_seqs.to(device), tgt_seqs.to(device)
            outputs = model(
                src_seqs, tgt_seqs, teacher_forcing_ratio=teacher_forcing_ratio
            )
            if not FORCE_DATA_TO_FLOAT32:
                outputs = outputs.double()
            loss = criterion(
                outputs,
                utils.prepare_tgt_seqs(args.architecture, src_seqs, tgt_seqs),
            )
            #add a small eps to loss
            loss += 1e-6
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
        epoch_loss = epoch_loss / num_training_sequences
        training_losses.append(epoch_loss)
        val_loss = generate.eval(
            model, criterion, dataset["validation"], args.batch_size, device,
        )
        val_losses.append(val_loss)
        opt.epoch_step(val_loss=val_loss)
        logging.info(
            f"Training loss {epoch_loss} | "
            f"Validation loss {val_loss} | "
            f"Iterations {iterations + 1}"
        )
        epoch_time = int((time.perf_counter() - start_time) / (epoch + 1))
        logging.info(f"Average epoch time: {pretty_time_delta(epoch_time)}. {pretty_time_delta((args.epochs - (epoch + 1)) * epoch_time)} estimated left.")
        if epoch % args.save_model_frequency == 0:
            _, mae = test.test_model(
                model=model,
                dataset=dataset["validation"],
                rep=args.representation,
                device=device,
                mean=mean,
                std=std,
                max_len=tgt_len,
            )
            logging.info(f"Validation MAE: {mae}")
            torch.save(
                model.state_dict(), f"{args.save_model_path}/{epoch}.model"
            )
            if len(val_losses) == 0 or val_loss <= min(val_losses):
                torch.save(
                    model.state_dict(), f"{args.save_model_path}/best.model"
                )
    return training_losses, val_losses


def plot_curves(args, training_losses, val_losses):
    plt.plot(range(len(training_losses)), training_losses)
    plt.plot(range(len(val_losses)), val_losses)
    plt.ylabel("MSE Loss")
    plt.xlabel("Epoch")
    plt.savefig(f"{args.save_model_path}/loss.svg", format="svg")


def main(args):
    train_losses, val_losses = train(args)
    plot_curves(args, train_losses, val_losses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sequence to sequence motion prediction training"
    )
    parser.add_argument(
        "--preprocessed-path",
        type=str,
        help="Path to folder with pickled " "files",
        required=True,
    )
    parser.add_argument(
        "--batch-size", type=int, help="Batch size for training", default=64
    )
    parser.add_argument(
        "--shuffle", action='store_true',
        help="Use this option to enable shuffling",
    )
    parser.add_argument(
        "--hidden-dim",
        type=int,
        help="Hidden size of LSTM units in encoder/decoder",
        default=1024,
    )
    parser.add_argument(
        "--num-layers",
        type=int,
        help="Number of layers of LSTM/Transformer in encoder/decoder",
        default=1,
    )
    parser.add_argument(
        "--save-model-path",
        type=str,
        help="Path to store saved models",
        required=True,
    )
    parser.add_argument(
        "--save-model-frequency",
        type=int,
        help="Frequency (in terms of number of epochs) at which model is "
        "saved",
        default=5,
    )
    parser.add_argument(
        "--epochs", type=int, help="Number of training epochs", default=200
    )
    parser.add_argument(
        "--device",
        type=str,
        help="Training device",
        default=None,
        choices=["cpu", "cuda"],
    )
    parser.add_argument(
        "--architecture",
        type=str,
        help="Seq2Seq archtiecture to be used",
        default="seq2seq",
        choices=[
            "seq2seq",
            "tied_seq2seq",
            "transformer",
            "transformer_encoder",
            "rnn",
        ],
    )
    parser.add_argument(
        "--lr", type=float, help="Learning rate", default=None,
    )
    parser.add_argument(
        "--optimizer",
        type=str,
        help="Torch optimizer",
        default="sgd",
        choices=["adam", "sgd", "noamopt"],
    )
    args = parser.parse_args()
    main(args)
