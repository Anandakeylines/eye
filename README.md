# OCT Medical Image Classification Model

A state-of-the-art deep learning system for classifying retinal OCT images into 16 disease categories using transfer learning.

## 📊 Dataset Overview

- **Total Images**: 408
- **Categories**: 16 (DR. KNI CF, OCT SRF, OCT CME, PED variants, etc.)
- **Train/Val/Test Split**: 70% / 15% / 15%

## 🧠 Model Architecture

- **Base Model**: EfficientNet-B0 (pretrained on ImageNet)
- **Approach**: Transfer Learning with fine-tuning
- **Optimizer**: AdamW with learning rate scheduling
- **Loss Function**: CrossEntropyLoss
- **Features**:
  - Frozen early layers (feature extraction)
  - Trainable custom classifier head
  - Data augmentation (rotation, flipping, affine transforms)
  - Early stopping (prevents overfitting)
  - Batch normalization & dropout

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

For GPU support (optional but recommended):

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Train the Model

```bash
python train_model.py
```

**What happens:**

- Loads 408 images from 16 folders
- Splits into train/val/test
- Trains for up to 50 epochs with early stopping
- Saves best model as `best_model.pth`
- Generates performance visualizations

**Training time**: ~10-30 minutes (depends on GPU)

### 3. Use for Predictions

```python
from inference import OCTInference

# Load model
predictor = OCTInference()

# Single prediction
result = predictor.predict('path/to/image.jpg')
print(result['predictions'][0]['class'])  # Top prediction

# Visualize
predictor.visualize_prediction('path/to/image.jpg')

# Batch prediction
results = predictor.predict_batch(['image1.jpg', 'image2.jpg', 'image3.jpg'])
```

## 📁 Output Files

After training:

- **best_model.pth** - Best model weights during training
- **final_model.pth** - Final trained model
- **model_metadata.json** - Model classes and config
- **training_history.png** - Loss/accuracy graphs
- **confusion_matrix.png** - Prediction accuracy by class

After inference:

- **prediction_result.png** - Visualization with predictions

## 📈 Performance Metrics

The model outputs:

- **Test Accuracy**: Overall accuracy on unseen test images
- **Per-class Precision/Recall/F1**: Detailed metrics for each condition
- **Confusion Matrix**: Shows which classes are confused

## 🔧 Configuration

Edit `CONFIG` in `train_model.py` to customize:

```python
CONFIG = {
    'data_path': 'Krishnendu PCV',      # Data folder path
    'batch_size': 16,                   # Training batch size
    'epochs': 50,                       # Max epochs
    'learning_rate': 0.001,             # Learning rate
    'image_size': 224,                  # Input image size
    'train_split': 0.7,                 # 70% train
    'val_split': 0.15,                  # 15% val
    'test_split': 0.15,                 # 15% test
}
```

## 💡 Tips for Better Performance

1. **More Data**: Collect more images (~500+ per class for better generalization)
2. **Data Quality**: Ensure consistent image quality and proper labeling
3. **Fine-tuning**: Unfreeze more layers for better adaptation:
   ```python
   for param in model.features[:3].parameters():  # Lower is more frozen
       param.requires_grad = False
   ```
4. **Ensemble**: Train multiple models and combine predictions
5. **Augmentation**: Increase augmentation strength for limited data

## 🐛 Troubleshooting

**GPU not working:**

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If False, use CPU only (slower but works)

**Out of memory:**

```bash
# Reduce batch size in CONFIG
'batch_size': 8  # instead of 16
```

**Low accuracy:**

- Check image quality
- Verify folder structure matches data_path
- Increase epochs or learning rate
- Add more data augmentation

## 📚 Understanding Results

### Confusion Matrix

- Diagonal = correct predictions
- Off-diagonal = misclassifications
- Shows which diseases are confused with each other

### Classification Report

- **Precision**: Of predicted X, how many are actually X
- **Recall**: Of true X, how many were found
- **F1-Score**: Harmonic mean (0-1, higher is better)

## 🔬 Advanced Usage

### Custom Prediction on Folder

```python
from inference import OCTInference
from pathlib import Path

predictor = OCTInference()
for image_path in Path('Krishnendu PCV').rglob('*.jpg'):
    result = predictor.predict(str(image_path))
    print(f"{image_path.name}: {result['predictions'][0]}")
```

### Export Model for Production

```python
# Convert to ONNX for deployment
import torch.onnx
dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(model, dummy_input, "model.onnx")
```

## 📞 Support

For issues or questions:

1. Check GPU status
2. Verify data paths
3. Review console output for errors
4. Check README sections above

---

**Created**: March 2026
**Model**: EfficientNet-B0 + Transfer Learning
**Framework**: PyTorch 2.0+
