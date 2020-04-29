import torch

#global parameters

TOTAL_STEPS = 20

#use cuda?
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#gready actions
EPS_START = 0.9
EPS_END = 0.0
EPS_DECAY = 10000
