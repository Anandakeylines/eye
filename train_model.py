"""
Multi-label OCT medical image classification training script.
"""

import copy
import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.optim as optim
from PIL import Image
from sklearn.metrics import (
    classification_report,
    f1_score,
    hamming_loss,
    multilabel_confusion_matrix,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset, Subset

from analyze_data import REPORT_KEYWORDS
from model_utils import (
    DEFAULT_BEST_MODEL_PATH,
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    IMAGE_SIZE,
    build_inference_transform,
    build_model,
    build_train_transform,
)

CONFIG = {
    "data_paths": [str(Path(__file__).resolve().parent / "Krishnendu PCV")],
    "batch_size": 16,
    "epochs": 25,
    "learning_rate": 0.0005,
    "weight_decay": 1e-4,
    "model_name": "EfficientNet-B0",
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "image_size": IMAGE_SIZE,
    "train_split": 0.7,
    "val_split": 0.15,
    "test_split": 0.15,
    "random_seed": 42,
    "prediction_threshold": 0.35,
}


class TransformedSubset(Dataset):
    """Apply a transform to a dataset subset."""

    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, index):
        image, target = self.subset[index]
        if self.transform is not None:
            image = self.transform(image)
        return image, target


class MultiLabelOCTDataset(Dataset):
    """Group duplicated images into one sample with multiple labels."""

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

    def __init__(self, root_paths):
        self.root_paths = [Path(root) for root in root_paths]
        self.samples = []
        self.classes = []
        self.class_to_idx = {}
        self._build_index()

    def _build_index(self):
        existing_roots = [root for root in self.root_paths if root.exists()]
        if not existing_roots:
            missing = ", ".join(str(root) for root in self.root_paths)
            raise FileNotFoundError(f"Dataset folder(s) not found: {missing}")

        grouped = {}
        class_names = set()

        for root in existing_roots:
            for class_dir in sorted(path for path in root.iterdir() if path.is_dir()):
                class_names.add(class_dir.name)
                for image_path in sorted(class_dir.rglob("*")):
                    if not image_path.is_file():
                        continue
                    if image_path.suffix.lower() not in self.IMAGE_EXTENSIONS:
                        continue
                    if any(keyword in image_path.name.lower() for keyword in REPORT_KEYWORDS):
                        continue

                    entry = grouped.setdefault(
                        image_path.name,
                        {"path": image_path, "labels": set()},
                    )
                    entry["labels"].add(class_dir.name)

        self.classes = sorted(class_names)
        self.class_to_idx = {name: idx for idx, name in enumerate(self.classes)}

        for image_name, entry in sorted(grouped.items()):
            target = torch.zeros(len(self.classes), dtype=torch.float32)
            for label_name in entry["labels"]:
                target[self.class_to_idx[label_name]] = 1.0
            self.samples.append((entry["path"], target))

        if not self.samples:
            raise ValueError("No usable OCT images found after excluding report-style images.")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        image_path, target = self.samples[index]
        image = Image.open(image_path).convert("RGB")
        return image, target.clone()


class OCTDataset:
    """Handle dataset loading and splitting."""

    @staticmethod
    def get_transforms():
        return (
            build_train_transform(CONFIG["image_size"]),
            build_inference_transform(CONFIG["image_size"]),
        )

    @staticmethod
    def load_data():
        train_transforms, eval_transforms = OCTDataset.get_transforms()
        full_dataset = MultiLabelOCTDataset(CONFIG["data_paths"])

        print("\nDataset Summary:")
        print(f"Total usable images: {len(full_dataset)}")
        print(f"Number of classes: {len(full_dataset.classes)}")
        print(f"Classes: {full_dataset.classes}\n")

        indices = list(range(len(full_dataset)))
        train_indices, temp_indices = train_test_split(
            indices,
            test_size=(1 - CONFIG["train_split"]),
            random_state=CONFIG["random_seed"],
            shuffle=True,
        )

        val_ratio = CONFIG["val_split"] / (CONFIG["val_split"] + CONFIG["test_split"])
        val_indices, test_indices = train_test_split(
            temp_indices,
            test_size=(1 - val_ratio),
            random_state=CONFIG["random_seed"],
            shuffle=True,
        )

        train_dataset = TransformedSubset(Subset(full_dataset, train_indices), train_transforms)
        val_dataset = TransformedSubset(Subset(full_dataset, val_indices), eval_transforms)
        test_dataset = TransformedSubset(Subset(full_dataset, test_indices), eval_transforms)

        print(
            f"Train: {len(train_indices)} | Val: {len(val_indices)} | Test: {len(test_indices)}\n"
        )

        return train_dataset, val_dataset, test_dataset, full_dataset


class OCTModel:
    """Build and train the multi-label OCT model."""

    def __init__(self, num_classes):
        self.device = torch.device(CONFIG["device"])
        self.num_classes = num_classes
        self.history = {"train_loss": [], "val_loss": []}
        self.model = self.build_model()

    def build_model(self):
        print("Building EfficientNet-B0 model...")
        model = build_model(self.num_classes, pretrained=True)
        for param in model.features[:5].parameters():
            param.requires_grad = False
        return model.to(self.device)

    def run_epoch(self, dataloader, criterion, optimizer=None):
        is_train = optimizer is not None
        self.model.train(mode=is_train)
        total_loss = 0.0

        for images, labels in dataloader:
            images = images.to(self.device)
            labels = labels.to(self.device)

            outputs = self.model(images)
            loss = criterion(outputs, labels)

            if is_train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            total_loss += loss.item()

        return total_loss / len(dataloader)

    def train(self, train_loader, val_loader, pos_weight):
        criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight.to(self.device))
        optimizer = optim.AdamW(
            self.model.parameters(),
            lr=CONFIG["learning_rate"],
            weight_decay=CONFIG["weight_decay"],
        )
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=4)

        best_val_loss = float("inf")
        patience_counter = 0

        print("Starting training...\n")

        for epoch in range(CONFIG["epochs"]):
            train_loss = self.run_epoch(train_loader, criterion, optimizer)
            val_loss = self.run_epoch(val_loader, criterion)

            self.history["train_loss"].append(train_loss)
            self.history["val_loss"].append(val_loss)
            scheduler.step(val_loss)

            print(
                f"Epoch [{epoch + 1}/{CONFIG['epochs']}] "
                f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}"
            )

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                torch.save(self.model.state_dict(), DEFAULT_BEST_MODEL_PATH)
            else:
                patience_counter += 1
                if patience_counter >= 8:
                    print(f"Early stopping at epoch {epoch + 1}")
                    break

        self.model.load_state_dict(torch.load(DEFAULT_BEST_MODEL_PATH, map_location=self.device))
        print("Training completed!")
        return self.history


def evaluate_model(model, test_loader, class_names, device, threshold):
    """Evaluate a multi-label model on the test set."""
    print("\nEvaluating model on test set...\n")

    model.eval()
    all_probs = []
    all_labels = []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            outputs = model(images)
            probs = torch.sigmoid(outputs).cpu()
            all_probs.append(probs)
            all_labels.append(labels)

    y_prob = torch.cat(all_probs).numpy()
    y_true = torch.cat(all_labels).numpy()
    y_pred = (y_prob >= threshold).astype(int)

    micro_f1 = f1_score(y_true, y_pred, average="micro", zero_division=0)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    loss = hamming_loss(y_true, y_pred)

    print(f"Micro F1: {micro_f1:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Hamming Loss: {loss:.4f}\n")

    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=class_names, zero_division=0))

    matrices = multilabel_confusion_matrix(y_true, y_pred)
    matrix = []
    for idx, class_name in enumerate(class_names):
        tn, fp, fn, tp = matrices[idx].ravel()
        matrix.append([tp, fp, fn, tn])

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["TP", "FP", "FN", "TN"],
        yticklabels=class_names,
    )
    plt.title("Per-Class Confusion Summary")
    plt.tight_layout()
    plt.savefig("confusion_matrix.png", dpi=150, bbox_inches="tight")
    print("Confusion summary saved as 'confusion_matrix.png'")

    return {
        "micro_f1": float(micro_f1),
        "macro_f1": float(macro_f1),
        "hamming_loss": float(loss),
    }


def plot_training_history(history):
    """Plot training history."""
    plt.figure(figsize=(8, 5))
    plt.plot(history["train_loss"], label="Train Loss", linewidth=2)
    plt.plot(history["val_loss"], label="Val Loss", linewidth=2)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Validation Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("training_history.png", dpi=150, bbox_inches="tight")
    print("Training history saved as 'training_history.png'")


def main():
    print("=" * 60)
    print("MULTI-LABEL OCT MEDICAL IMAGE CLASSIFICATION MODEL")
    print("=" * 60)
    print("\nConfiguration:")
    for key, value in CONFIG.items():
        print(f"  {key}: {value}")

    train_dataset, val_dataset, test_dataset, full_dataset = OCTDataset.load_data()

    train_loader = DataLoader(train_dataset, batch_size=CONFIG["batch_size"], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG["batch_size"], shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=CONFIG["batch_size"], shuffle=False)

    train_targets = torch.stack([full_dataset.samples[i][1] for i in train_dataset.subset.indices])
    positive_counts = train_targets.sum(dim=0)
    negative_counts = len(train_targets) - positive_counts
    pos_weight = negative_counts / positive_counts.clamp_min(1.0)

    model_handler = OCTModel(num_classes=len(full_dataset.classes))
    history = model_handler.train(train_loader, val_loader, pos_weight)

    plot_training_history(history)

    device = torch.device(CONFIG["device"])
    metrics = evaluate_model(
        model_handler.model,
        test_loader,
        full_dataset.classes,
        device,
        CONFIG["prediction_threshold"],
    )

    torch.save(model_handler.model.state_dict(), DEFAULT_MODEL_PATH)

    metadata = {
        "model": CONFIG["model_name"],
        "task_type": "multi_label",
        "num_classes": len(full_dataset.classes),
        "classes": full_dataset.classes,
        "prediction_threshold": CONFIG["prediction_threshold"],
        "metrics": metrics,
        "created": datetime.now().isoformat(),
        "config": copy.deepcopy(CONFIG),
    }

    with open(DEFAULT_METADATA_PATH, "w") as handle:
        json.dump(metadata, handle, indent=4)

    print("\n" + "=" * 60)
    print("All files saved:")
    print("  - final_model.pth")
    print("  - model_metadata.json")
    print("  - training_history.png")
    print("  - confusion_matrix.png")
    print("=" * 60)


if __name__ == "__main__":
    main()
