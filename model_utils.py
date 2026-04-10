"""
Shared model and preprocessing utilities for OCT classification.
"""

from pathlib import Path

import torch.nn as nn
from torchvision import transforms
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

IMAGE_SIZE = 224
NORMALIZE_MEAN = EfficientNet_B0_Weights.IMAGENET1K_V1.transforms().mean
NORMALIZE_STD = EfficientNet_B0_Weights.IMAGENET1K_V1.transforms().std
MODEL_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = MODEL_DIR / "final_model.pth"
DEFAULT_METADATA_PATH = MODEL_DIR / "model_metadata.json"
DEFAULT_BEST_MODEL_PATH = MODEL_DIR / "best_model.pth"


def create_classifier(model, num_classes):
    """Attach the custom classifier head used across training and inference."""
    in_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.5),
        nn.Linear(in_features, 512),
        nn.BatchNorm1d(512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, 256),
        nn.BatchNorm1d(256),
        nn.ReLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes),
    )
    return model


def build_model(num_classes, pretrained=False):
    """Build the EfficientNet-B0 model with the project classifier head."""
    weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
    model = efficientnet_b0(weights=weights)
    return create_classifier(model, num_classes)


def build_inference_transform(image_size=IMAGE_SIZE):
    """Preprocessing used for validation, test, API, and local inference."""
    return transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
        ]
    )


def build_train_transform(image_size=IMAGE_SIZE):
    """Training-time augmentations."""
    return transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size, scale=(0.85, 1.0)),
            transforms.RandomHorizontalFlip(p=0.3),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
            transforms.ToTensor(),
            transforms.Normalize(mean=NORMALIZE_MEAN, std=NORMALIZE_STD),
        ]
    )
