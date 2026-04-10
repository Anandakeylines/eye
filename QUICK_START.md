# Quick Start Guide

## What You Have

✅ **Best OCT Classification Model** with:

- EfficientNet-B0 (state-of-the-art efficiency)
- Transfer Learning (fast training, high accuracy)
- Data Augmentation (prevent overfitting)
- Early Stopping (avoid wasted training)
- 408 medical images ready to use

## Files Created

1. **train_model.py** - Main training script
2. **inference.py** - Make predictions on new images
3. **analyze_data.py** - Explore your dataset
4. **requirements.txt** - Python dependencies
5. **README.md** - Full documentation
6. **This file** - Quick start

## 3-Step Setup

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Analyze Your Data (Optional)

```bash
python analyze_data.py
```

This generates:

- Class statistics
- Sample visualization
- Dataset recommendations

### Step 3: Train the Model

```bash
python train_model.py
```

**Wait for training to complete** (~15-30 minutes)

Output files:

- `best_model.pth` - Best performing model
- `final_model.pth` - Final trained weights
- `training_history.png` - Accuracy/loss graphs
- `confusion_matrix.png` - Per-class performance
- `model_metadata.json` - Model info

## Make Predictions

### Option A: Python Code

```python
from inference import OCTInference

predictor = OCTInference()
result = predictor.predict('path/to/image.jpg')
print(result['predictions'][0]['class'])  # Top prediction

# With visualization
predictor.visualize_prediction('path/to/image.jpg')
```

### Option B: Batch Predictions

```python
from inference import OCTInference

predictor = OCTInference()
images = ['img1.jpg', 'img2.jpg', 'img3.jpg']
results = predictor.predict_batch(images)
```

## Expected Results

- **Test Accuracy**: 75-90% (depends on data quality)
- **Training Time**: 15-30 minutes on CPU, 5-10 on GPU
- **Model Size**: ~80 MB

## GPU Support (Optional but Faster)

If NVIDIA GPU available:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

Training will be **5-10x faster**

## Next Steps

1. ✅ Install dependencies
2. ✅ Analyze data (python analyze_data.py)
3. ✅ Train model (python train_model.py)
4. ✅ Make predictions (see examples above)
5. ✅ Fine-tune (edit CONFIG in train_model.py)

## Troubleshooting

| Issue                        | Solution                                            |
| ---------------------------- | --------------------------------------------------- |
| `ModuleNotFoundError: torch` | Run `pip install -r requirements.txt`               |
| `CUDA out of memory`         | Reduce batch_size from 16 to 8 in train_model.py    |
| `Low accuracy`               | Collect more images or enable stronger augmentation |
| `Slow training`              | Install GPU drivers and pytorch-cuda                |

## Key Concepts

**Transfer Learning**: Using a pre-trained model (ImageNet) as starting point. Much faster and better than training from scratch with small datasets.

**EfficientNet-B0**: State-of-the-art architecture that's fast and accurate. Good balance for medical imaging.

**Data Augmentation**: Artificially creates variations (rotate, flip, etc.) to prevent overfitting with limited data.

**Confusion Matrix**: Shows which diseases your model confuses. Diagonal = correct predictions.

## Questions?

- Check **README.md** for detailed documentation
- Look at console output during training for errors
- See Python comments in code files

---

**Ready? Run:** `python train_model.py`
