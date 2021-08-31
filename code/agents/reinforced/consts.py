import argparse
import os
import torch

initialized: bool = False

NUM_CORES: int = max(1, os.environ.get('NUM_CORES', os.cpu_count() - 1))

USE_GPU: bool = torch.cuda.is_available()
NUM_GPUS: int = os.environ.get('NUM_GPUS', torch.cuda.device_count())

if not initialized:
    p = argparse.ArgumentParser()
    p.add_argument('-c', '--cores', help="max num of cores to use", type=int, default=NUM_CORES)
    p.add_argument('-g', '--gpus', help="max num of gpus to use", type=int, default=NUM_GPUS)
    args = p.parse_args()

    NUM_CORES = args.cores
    NUM_GPUS = args.gpus

FRAC_GPUS: float = NUM_GPUS / NUM_CORES
