# React OCT Image Classifier

A complete web application for uploading and classifying OCT medical images using a trained deep learning model.

## 🎯 Features

✅ **Drag & Drop Upload** - Easy image upload interface
✅ **Real-time Predictions** - Instant classification results
✅ **Confidence Scores** - See confidence for each prediction
✅ **Beautiful UI** - Modern, responsive design
✅ **All Classes** - Predicts all 16 disease categories
✅ **Fast Processing** - GPU-accelerated predictions

## 📋 Prerequisites

Before running the React app, you need:

1. **Trained Model** - Run `python train_model.py` first
2. **Node.js** - Download from https://nodejs.org (v14+)
3. **Flask Backend** - API server for predictions

## 🚀 Setup & Run

### Step 1: Install Node.js

Download from https://nodejs.org and install (includes npm)

Verify installation:

```bash
node --version
npm --version
```

### Step 2: Install Dependencies

Navigate to react-app folder:

```bash
cd react-app
npm install
```

This installs:

- React
- Axios (for HTTP requests)
- React Scripts (build tools)

### Step 3: Start the Servers

**Terminal 1 - Start Flask Backend** (in main folder):

```bash
python api_server.py
```

Expected output:

```
✅ Model ready on cuda
🚀 Starting Flask server...
   API: http://localhost:5000
   Frontend: http://localhost:3000
```

**Terminal 2 - Start React Frontend** (in react-app folder):

```bash
npm start
```

Expected output:

```
webpack compiled successfully
Local:      http://localhost:3000
```

### Step 4: Open in Browser

Browser will automatically open http://localhost:3000

## 📸 How to Use

1. **Upload Image**
   - Drag and drop an OCT image
   - Or click to browse and select

2. **Get Predictions**
   - Model processes image automatically
   - See top prediction and confidence
   - View all predictions with percentages

3. **Upload Another**
   - Click "Clear & Upload Another"
   - Repeat process

## 🔧 Configuration

### Backend (Flask)

Edit `api_server.py` to change:

- Port: Change `app.run(debug=True, port=5000)` to different port
- Device: Auto-detects GPU, can override in `load_model()`

### Frontend (React)

Edit `src/App.js` to change:

- API URL: Change `fetch('http://localhost:5000/predict'...)`
- Styling: Edit `src/App.css` and component CSS files

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: Flask"

**Solution:**

```bash
pip install -r api_requirements.txt
```

### Issue: "Cannot find module 'react'"

**Solution:**

```bash
cd react-app
npm install
```

### Issue: "Failed to fetch from http://localhost:5000"

**Solution:**

1. Check Flask server is running
2. Check port 5000 is not blocked
3. Check CORS is enabled in api_server.py

### Issue: "Model not found"

**Solution:**

1. Make sure you trained the model: `python train_model.py`
2. Check `final_model.pth` and `model_metadata.json` exist
3. Run api_server.py from main folder

### Issue: Slow predictions

**Solution:**

- Enable GPU support with CUDA
- Use GPU-accelerated PyTorch:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

## 📁 File Structure

```
react-app/
├── public/
│   └── index.html              # HTML entry point
├── src/
│   ├── components/
│   │   ├── ImageUploader.js    # Upload component
│   │   └── ImageUploader.css   # Upload styles
│   ├── App.js                  # Main app component
│   ├── App.css                 # App styles
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies
└── .gitignore                  # Git ignore rules

../
├── api_server.py               # Flask API server
├── api_requirements.txt         # Backend dependencies
├── train_model.py              # Model training script
├── final_model.pth             # Trained weights
└── model_metadata.json         # Model info
```

## 🌐 API Endpoints

The Flask backend provides:

### GET /health

Health check

```json
{
  "status": "healthy",
  "device": "cuda",
  "num_classes": 16
}
```

### GET /info

Model information

```json
{
  "model": "EfficientNet-B0",
  "num_classes": 16,
  "classes": [...],
  "test_accuracy": 0.85
}
```

### POST /predict

Make prediction (multipart/form-data)

```json
{
  "predictions": [
    {
      "class": "OCT SRF",
      "probability": 0.925,
      "percentage": 92.5
    },
    ...
  ],
  "top_prediction": "OCT SRF",
  "confidence": 92.5
}
```

## 🎨 Customization

### Change Colors

Edit `src/App.css`:

```css
/* Gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Change Title

Edit `src/App.js` header section:

```jsx
<h1>🏥 Your Custom Title</h1>
```

### Add More Categories

Edit `src/components/ImageUploader.js` categories:

```jsx
<div className="category">Your Category</div>
```

## 📦 Build for Production

Create optimized build:

```bash
npm run build
```

Output in `build/` folder - ready for deployment

Deploy to services like:

- Vercel
- Netlify
- AWS S3 + CloudFront
- Docker container

## 🚀 Advanced Usage

### Run Without Auto-Open Browser

```bash
npm start -- --no-browser
```

### Build and Test Production Build

```bash
npm run build
npm install -g serve
serve -s build
```

### Enable Development Tools

Add to `src/index.js`:

```javascript
if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
  window.__REACT_DEVTOOLS_GLOBAL_HOOK__.isDisabled = false;
}
```

## 📚 Resources

- React Docs: https://react.dev
- Flask Docs: https://flask.palletsprojects.com
- PyTorch Docs: https://pytorch.org/docs
- OAuth/Auth: Add authentication middleware

## 💡 Next Steps

1. ✅ Setup Node.js
2. ✅ Run `npm install` in react-app
3. ✅ Start Flask backend: `python api_server.py`
4. ✅ Start React frontend: `npm start`
5. ✅ Upload images and get predictions!

## 📞 Support

For issues:

1. Check all three files exist (final_model.pth, model_metadata.json, api_server.py)
2. Verify both servers are running on correct ports
3. Check browser console (F12) for errors
4. Check terminal output for error messages

---

**Enjoy your OCT classification app! 🎉**
