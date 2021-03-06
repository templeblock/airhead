#     ___   _     __               __
#    / _ | (_)___/ /  ___ ___ ____/ /
#   / __ |/ / __/ _ \/ -_) _ `/ _  /
#  /_/ |_/_/_/ /_//_/\__/\_,_/\_,_/
#

"""
Lightning wrapper for model, to facilitate training
"""

import torch.nn.functional as F
from torch import nn
from torch import optim
from pytorch_lightning.core import LightningModule
from time import time

####################################
# Lightning wrapper for UNet model #
####################################

class UNetLightning(LightningModule):
    def __init__(
        self,
        network,
        network_params=None,
        loss=F.cross_entropy,
        loss_params=None,
        metrics=(F.cross_entropy,),
        metrics_params=None,
        optimizer=optim.SGD,
        optimizer_params=None,
        scheduler=optim.lr_scheduler.ReduceLROnPlateau,
        scheduler_params=None,
        scheduler_config=None,
        inference=nn.Identity,
        inference_params=None,
            test_inference=None,
            test_inference_params=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Network parameters
        self.network_params = {} if network_params is None else network_params

        # Initialize network
        self.net = network(**self.network_params)

        # Set loss
        self.loss = loss
        self.loss_params = {} if loss_params is None else loss_params

        # Set metrics
        self.metrics = metrics
        n_metrics = len(self.metrics)
        self.metrics_params = (
            [{}] * n_metrics if metrics_params is None else metrics_params
        )

        # Set optimizer
        self.optimizer = optimizer
        self.optimizer_params = (
            {} if optimizer_params is None else optimizer_params
        )

        # Set learning rate scheduler
        if scheduler is not None:
            self.scheduler = scheduler
            self.scheduler_params = (
                {} if scheduler_params is None else scheduler_params
            )
            self.scheduler_config = (
                {} if scheduler_config is None else scheduler_config
            )

        # Set inference methods
        self.inference = inference
        self.inference_params = (
            {} if inference_params is None else inference_params
        )
        self.test_inference = test_inference
        self.test_inference_params = (
            {} if test_inference_params is None else test_inference_params
        )

        # Test results
        self.test_results = None

        # Save hyperparameters
        self.save_hyperparameters()

    # Get total number of learnable weights
    def get_n_parameters(self):
        return sum(p.numel() for p in self.net.parameters() if p.requires_grad)

    # Feedforward
    def forward(self, x):
        return self.net(x)

    # Configure optimization and LR schedule
    def configure_optimizers(self):
        optimizer = self.optimizer(
            self.net.parameters(), **self.optimizer_params
        )
        if hasattr(self, "scheduler"):
            scheduler = self.scheduler(optimizer, **self.scheduler_params)
            config = (
                [optimizer],
                [{"scheduler": scheduler, **self.scheduler_config}],
            )
        else:
            config = [optimizer]

        return config

    ############
    # Training #
    ############

    # Training step
    def training_step(self, batch, batch_idx):

        # Get new input and predict, then calculate loss
        x, y = batch["input"], batch["target"]
        y_hat = self(x)
        loss = self.loss(y_hat, y, **self.loss_params)

        # Log output and calculate metrics
        self.log(f"train_{self.loss.__name__}", loss, prog_bar=True)
        return loss

    # Training epoch end
    def training_epoch_end(self, outputs):

        # Metrics we'll log
        metrics_dict = dict.fromkeys(outputs[0])

        # Loop over metrics
        for metric_name in metrics_dict:

            # Average metric over outputs within epoch
            metric_total = 0.0
            for output in outputs:
                metric_total += output[metric_name]
            metric_value = metric_total / len(outputs)

            if hasattr(metric_value, "item"):
                metric_value = metric_value.item()
            self.log(metric_name, metric_value, prog_bar=True)

            # Log using Tensorboard logger TODO: Check if this is necessary, and how this compares to self.log
            self.logger.experiment.add_scalar(f"{metric_name}/train", metric_value, self.current_epoch)

    # Validation step
    def validation_step(self, batch, batch_idx):

        # Get new input and predict, then calculate loss
        x, y = batch["input"], batch["target"]

        y_hat = self.inference(x, self, **self.inference_params)

        # Calculate metrics
        output = {}
        for m, pars in zip(self.metrics, self.metrics_params):
            output[f"val_{m.__name__}"] = m(y_hat, y, **pars)
        return output

    # Validation epoch end
    def validation_epoch_end(self, outputs):

        # Metrics we'll log
        metrics_dict = dict.fromkeys(outputs[0])

        # Loop over metrics
        for metric_name in metrics_dict:

            # Average metric over outputs within epoch
            metric_total = 0.0
            for output in outputs:
                metric_total += output[metric_name]
            metric_value = metric_total / len(outputs)

            if hasattr(metric_value, "item"):
                metric_value = metric_value.item()
            self.log(metric_name, metric_value, prog_bar=True)

            # Log using Tensorboard logger
            self.logger.experiment.add_scalar(f"{metric_name}/val",metric_value,self.current_epoch)

    # Test step
    def test_step(self, batch, batch_idx):

        # Get new input and predict, then calculate loss
        """x, y = batch["input"], batch["target"]
        y_hat = self.inference(x, self, **self.inference_params)

        # Calculate metrics
        output = {}
        for m, pars in zip(self.metrics, self.metrics_params):
            output[f"test_{m.__name__}"] = m(y_hat, y, **pars)
        return output"""

        # Get new input and predict, then calculate loss
        x, y, id = batch["input"], batch["target"], batch["id"]

        # Infer and time inference
        start = time()
        y_hat = self.test_inference(x, self, **self.test_inference_params)
        end = time()

        # Calculate metrics
        id = id[0] if len(id) == 1 else tuple(id)

        # Output dict with duration of inference
        output = {"id": id, "time": end - start}
        #output = {'time': end-start}

        # Add other metrics to output dict
        for m, pars in zip(self.metrics, self.metrics_params):

            metric_value = m(y_hat, y, **pars)

            if hasattr(metric_value, "item"):
                metric_value = metric_value.item()

            output[f"test_{m.__name__}"] = metric_value

        return output

    # Test epoch end (= test end)
    def test_epoch_end(self, outputs):
        self.test_results = outputs

