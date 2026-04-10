"""
Flask API server for multi-label OCT image classification.
"""

import io
import json
import sys

import torch
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image

from model_utils import (
    DEFAULT_METADATA_PATH,
    DEFAULT_MODEL_PATH,
    build_inference_transform,
    build_model,
)

app = Flask(__name__)
CORS(app)

model = None
metadata = None
device = None


def load_model():
    """Load the trained model and metadata."""
    global model, metadata, device

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    try:
        with open(DEFAULT_METADATA_PATH, "r") as handle:
            metadata = json.load(handle)
        print(f"Metadata loaded. Classes: {len(metadata['classes'])}")
    except FileNotFoundError:
        print("Error: model_metadata.json not found")
        print("Make sure you've trained the model first (python train_model.py)")
        sys.exit(1)

    model = build_model(metadata["num_classes"], pretrained=False)

    try:
        model.load_state_dict(torch.load(DEFAULT_MODEL_PATH, map_location=device))
        print("Model weights loaded")
    except FileNotFoundError:
        print("Error: final_model.pth not found")
        print("Make sure you've trained the model first (python train_model.py)")
        sys.exit(1)

    model = model.to(device)
    model.eval()
    print(f"Model ready on {device}")


def ensure_model_loaded():
    if model is None or metadata is None or device is None:
        raise RuntimeError("Model is not loaded.")


def get_transforms():
    return build_inference_transform()


def predict_probabilities(image):
    image_tensor = get_transforms()(image).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(image_tensor)
        probabilities = torch.sigmoid(logits)[0]
    return probabilities


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "device": str(device),
            "num_classes": metadata["num_classes"] if metadata else None,
            "task_type": metadata.get("task_type", "single_label") if metadata else None,
        }
    )


@app.route("/predict", methods=["POST"])
def predict():
    try:
        ensure_model_loaded()

        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        try:
            image = Image.open(io.BytesIO(file.read())).convert("RGB")
        except Exception as exc:
            return jsonify({"error": f"Invalid image file: {exc}"}), 400

        probabilities = predict_probabilities(image)
        ranked_indices = torch.argsort(probabilities, descending=True)
        threshold = metadata.get("prediction_threshold", 0.35)

        predictions = []
        for idx in ranked_indices:
            class_idx = int(idx)
            prob = float(probabilities[class_idx])
            predictions.append(
                {
                    "class": metadata["classes"][class_idx],
                    "probability": prob,
                    "percentage": prob * 100,
                    "detected": prob >= threshold,
                }
            )

        detected_labels = [item["class"] for item in predictions if item["detected"]]
        if not detected_labels:
            detected_labels = [predictions[0]["class"]]

        return jsonify(
            {
                "success": True,
                "task_type": metadata.get("task_type", "single_label"),
                "threshold": threshold,
                "detected_labels": detected_labels,
                "predictions": predictions,
                "top_prediction": predictions[0]["class"],
                "confidence": predictions[0]["percentage"],
            }
        )
    except Exception as exc:
        print(f"Error: {exc}")
        return jsonify({"error": f"Prediction failed: {exc}"}), 500


@app.route("/info", methods=["GET"])
def info():
    if not metadata:
        return jsonify({"error": "Model not loaded"}), 500

    return jsonify(
        {
            "model": metadata["model"],
            "task_type": metadata.get("task_type", "single_label"),
            "num_classes": metadata["num_classes"],
            "classes": metadata["classes"],
            "prediction_threshold": metadata.get("prediction_threshold"),
            "metrics": metadata.get("metrics", {}),
            "device": str(device),
        }
    )


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify(
            {
                "error": "Endpoint not found",
                "available_endpoints": [
                    "GET /health",
                    "GET /info",
                    "POST /predict",
                ],
            }
        ),
        404,
    )


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


load_model()


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("=" * 60)
    print("OCT IMAGE CLASSIFIER - Flask API SERVER")
    print("=" * 60)
    print(f"\nStarting Flask server on port {port}...")
    print("\nReady to receive predictions!\n")

    app.run(host="0.0.0.0", port=port, debug=False)