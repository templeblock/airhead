#     ___   _     __               __
#    / _ | (_)___/ /  ___ ___ ____/ /
#   / __ |/ / __/ _ \/ -_) _ `/ _  /
#  /_/ |_/_/_/ /_//_/\__/\_,_/\_,_/
#

"""
Main training script
"""

from os.path import join
from pytorch_lightning import Trainer
from pl_bolts.callbacks import PrintTableMetricsCallback
from pytorch_lightning.callbacks import LearningRateMonitor
from torch import optim

from helper import DATA_DIR, hi, log
from models.unet import UNet
from models.unet_lightning import UNetLightning
from training.data_module import BraTSDataModule
from training.inference import val_inference
from training.losses import dice_loss, dice_metric, dice_et, dice_tc, dice_wt
from training.utils import WarmupCosineSchedule

"""CONFIG = {
    "system_path": [],
    "data": {
        "datamodule": BraTSDataModule,
        "datamodule_params": {
            "data_dir": "~/MICCAI_BraTS2020_TrainingData",
            "validation_size": 0.2,
            "num_workers": 0,
            "batch_size": 1,
        },
    },
    "model": {
        "network": UNet,
        "network_params": {
            "in_channels": 4,
            "out_channels": 3,
            "encoder_depth": (1, 2, 2, 2, 2),
            "encoder_width": (32, 64, 128, 256, 320),
            "strides": (1, 2, 2, 2, 2),
            "decoder_depth": (2, 2, 2, 2),
            "upsample": "tconv",
            "block": unet.BasicBlock,
            "block_params": None,
        },
        "inference": val_inference,
        "inference_params": None,
    },
    "optimization": {
        "loss": dice_loss,
        "metrics": [dice_metric, dice_et, dice_tc, dice_wt],
        "optimizer": optim.AdamW,
        "optimizer_params": {"lr": 1e-4, "weight_decay": 1e-2},
        "scheduler": WarmupCosineSchedule,
        "scheduler_params": {"warmup_steps": 0, "total_steps": 100000},
        "scheduler_config": {"interval": "step"},
    },
    "training": {
        "max_steps": 100000,
        "max_epochs": 200,
        # "gpus": 1,
        # "num_nodes": 1,
        # "distributed_backend": "ddp",
        "callbacks": [
            LearningRateMonitor(logging_interval="step"),
            PrintTableMetricsCallback(),
        ],
    },
}"""

if __name__ == '__main__':

    # Let's go
    hi()
    # Set data directory
    root_dir = DATA_DIR
    train_dir = join(DATA_DIR, 'MICCAI_BraTS2020_TrainingData')
    test_dir = join(DATA_DIR, 'MICCAI_BraTS2020_ValidationData')

    # Initialize model
    log("Initializing UNet model")
    model = UNetLightning(

        # Architecture settings
        network=UNet,
        network_params={
            'in_channels': 4,
            'out_channels': 3,
            'widths': (32, 64, 128, 256, 320),
            'head': False},

        # Loss and metrics
        loss=dice_loss,
        metrics=[dice_metric, dice_et, dice_tc, dice_wt],

        # Optimizer
        optimizer=optim.AdamW,  # TODO: Why AdamW?
        optimizer_params={'lr': 1e-4, 'weight_decay': 1e-2},

        # Learning rate scheduler
        scheduler=WarmupCosineSchedule,
        scheduler_config={'interval': 'step'},
        scheduler_params={'warmup_steps': 0, 'total_steps': 1e5},

        # Inference method
        inference=val_inference,
        inference_params=None
    )

    # Initialize data module
    log("Initializing data module")
    brats = BraTSDataModule(data_dir=train_dir,
                            test_dir=test_dir,
                            num_workers=0,
                            batch_size=1,
                            validation_size=.2)

    # Initialize trainer
    log("Initializing trainer")
    trainer = Trainer(
        max_steps=100000,
        max_epochs=200,
        #gpus=1,
        #num_nodes=1,
        #distributed_backend='ddp',
        callbacks= [
            LearningRateMonitor(logging_interval="step"),
            PrintTableMetricsCallback(),
        ],
    )