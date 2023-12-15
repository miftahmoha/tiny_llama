from copy import deepcopy
from tqdm import tqdm

import torch
import matplotlib.pyplot as plt

from diagnosis import Diagnose
from training import TrainConfig, Trainer
from models import Llama


class GradDiagnose(Diagnose):
    def __init__(self, *, num_params_to_track: int, show_params_name: bool = False):
        self.num_params_to_track = num_params_to_track
        self.show_params_name = show_params_name

    def run(self, model: Llama, tokens: torch.Tensor, TRAIN_CONFIG: TrainConfig):

        legends = []

        model_clone = deepcopy(model)

        Trainer_ = Trainer(TRAIN_CONFIG)
        Trainer_.run(model_clone, tokens, hide_progress=True)

        for count, elem in tqdm(
            enumerate(model_clone.named_parameters()), total=self.num_params_to_track
        ):
            if elem[1].grad is not None:
                # Access the gradients for the parameter
                gradients = elem[1].grad

                hy, hx = torch.histogram(gradients.cpu(), density=True)
                plt.plot(hx[:-1].detach(), hy.detach())
                name = ".".join(elem[0].split(".")[-2:])

                if self.show_params_name:
                    legends.append(f"Param name: {name}")

                if count > self.num_params_to_track:
                    break

        plt.title("Gradient density")
        plt.legend(legends)
        plt.show()