"""
Inference script for multi-label OCT image prediction.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from PIL import Image

from model_utils import (
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    build_inference_transform,
    build_model,
)


class OCTInference:
    def __init__(self, model_path=DEFAULT_MODEL_PATH, metadata_path=DEFAULT_METADATA_PATH):
        model_path = Path(model_path)
        metadata_path = Path(metadata_path)

        with open(metadata_path, "r") as handle:
            self.metadata = json.load(handle)

        self.classes = self.metadata["classes"]
        self.num_classes = len(self.classes)
        self.threshold = self.metadata.get("prediction_threshold", 0.35)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print("Loading model...")
        self.model = build_model(self.num_classes, pretrained=False).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        self.transform = build_inference_transform()
        print(f"Model loaded. Ready to predict {self.num_classes} classes.\n")

    def predict(self, image_path, top_k=5):
        image_path = Path(image_path)
        image = Image.open(image_path).convert("RGB")
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(image_tensor)
            probabilities = torch.sigmoid(logits)[0]

        ranked_indices = torch.argsort(probabilities, descending=True)
        top_k = max(1, min(top_k, self.num_classes))

        predictions = [
            {
                "class": self.classes[int(idx)],
                "probability": float(probabilities[int(idx)]),
                "percentage": float(probabilities[int(idx)]) * 100,
            }
            for idx in ranked_indices[:top_k]
        ]
        detected_labels = [
            item["class"] for item in predictions if item["probability"] >= self.threshold
        ]

        if not detected_labels:
            detected_labels = [predictions[0]["class"]]

        return {
            "image_path": str(image_path),
            "threshold": self.threshold,
            "detected_labels": detected_labels,
            "predictions": predictions,
        }

    def visualize_prediction(self, image_path, save_path="prediction_result.png"):
        image = Image.open(image_path).convert("RGB")
        result = self.predict(image_path, top_k=len(self.classes))

        class_names = [item["class"] for item in result["predictions"]]
        scores = [item["percentage"] for item in result["predictions"]]
        colors = [
            "green" if item["class"] in result["detected_labels"] else "lightblue"
            for item in result["predictions"]
        ]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        ax1.imshow(image)
        ax1.set_title("Detected: " + ", ".join(result["detected_labels"]))
        ax1.axis("off")

        ax2.barh(class_names, scores, color=colors)
        ax2.set_xlabel("Probability (%)")
        ax2.set_title("Predicted Findings")
        ax2.set_xlim([0, 100])

        for idx, value in enumerate(scores):
            ax2.text(value + 1, idx, f"{value:.1f}%", va="center")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Prediction visualization saved as '{save_path}'")
        return result


if __name__ == "__main__":
    predictor = OCTInference()
    data_path = Path("Krishnendu PCV")
    image_files = [p for p in data_path.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp"}]

    if image_files:
        result = predictor.predict(str(image_files[0]))
        print("Detected:", ", ".join(result["detected_labels"]))
        predictor.visualize_prediction(str(image_files[0]))
    else:
        print("No images found in Krishnendu PCV folder")
