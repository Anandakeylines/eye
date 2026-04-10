# 🚀 Complete Startup Guide - React Web App

Follow these steps to get your OCT image classifier web app running in minutes!

## 📋 Checklist

- [ ] Python dependencies installed
- [ ] Model trained (final_model.pth exists)
- [ ] Node.js installed
- [ ] React dependencies installed
- [ ] Both servers running
- [ ] Tests completed

## Step 1: Train the Model (if not done yet)

```bash
python train_model.py
```

⏱️ Takes 15-30 minutes
✓ Creates: `final_model.pth`, `model_metadata.json`

## Step 2: Install Node.js

1. Download from https://nodejs.org (v16 or later)
2. Run installer and follow instructions
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

## Step 3: Install React Dependencies

In the main folder (where this file is):

```bash
cd react-app
npm install
```

Wait for installation to complete (~3-5 minutes)

## Step 4: Start Flask Backend

**Open Terminal 1** and run:

```bash
python api_server.py
```

You should see:

```
✅ Model ready on cuda
🚀 Starting Flask server...
   API: http://localhost:5000
```

**Keep this terminal open!**

## Step 5: Start React Frontend

**Open Terminal 2** (keep Terminal 1 running) and run:

```bash
cd react-app
npm start
```

You should see:

```
webpack compiled successfully
Local: http://localhost:3000
```

Browser will automatically open to http://localhost:3000

## Step 6: Test the App

1. ✅ See the purple header "OCT Medical Image Classifier"
2. ✅ See upload area with "Upload OCT Image"
3. ✅ See 16 category tags below
4. ✅ Drag & drop or click to upload an image
5. ✅ See predictions appear instantly

Example upload:

- Go to: `Krishnendu PCV` folder
- Pick any image from OCT folders
- Upload it
- See predictions!

## 🎯 Architecture

```
┌─────────────────────────────────────────┐
│        Your Browser (Port 3000)         │
│  React App with Upload & Results UI     │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP/POST (image file)
                 │
┌────────────────▼────────────────────────┐
│    Flask API Server (Port 5000)         │
│  - Receives image                       │
│  - Runs model prediction                │
│  - Returns results JSON                 │
└────────────────┬────────────────────────┘
                 │
                 │
┌────────────────▼────────────────────────┐
│    PyTorch Model (GPU/CPU)              │
│  - EfficientNet-B0                      │
│  - 16-class classification              │
│  - ~200ms prediction time               │
└─────────────────────────────────────────┘
```

## ⚡ Quick Commands Reference

| Task                 | Command                 | Terminal | Location         |
| -------------------- | ----------------------- | -------- | ---------------- |
| Train model          | `python train_model.py` | 1        | Main folder      |
| Start backend        | `python api_server.py`  | 1        | Main folder      |
| Start frontend       | `npm start`             | 2        | react-app folder |
| Install React deps   | `npm install`           | 2        | react-app folder |
| Build for production | `npm run build`         | 2        | react-app folder |

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 5000 is taken
netstat -ano | findstr :5000

# Or kill process and try again
pip install -r api_requirements.txt
python api_server.py
```

### Frontend won't start

```bash
# Clear cache and reinstall
cd react-app
rm -r node_modules
npm install
npm start
```

### "Cannot connect to backend"

- ✅ Backend running on Terminal 1?
- ✅ Backend shows "🚀 Starting Flask server"?
- ✅ Port 5000 not blocked by firewall?

### "Model not found"

- ✅ Run `python train_model.py` first
- ✅ Check files exist: `final_model.pth`, `model_metadata.json`
- ✅ Move api_server.py to folder with these files

## 📊 Expected Performance

| Aspect            | Value           |
| ----------------- | --------------- |
| Backend startup   | < 30 seconds    |
| React startup     | < 1 minute      |
| Image upload      | Instant display |
| Prediction        | 200-500ms       |
| Model size        | ~80 MB          |
| GPU memory needed | ~1 GB           |
| CPU memory needed | ~2 GB           |

## 🎨 What You Can Do

After it's running:

1. **Upload OCT Images**
   - From `Krishnendu PCV` folder
   - From camera/phone
   - Any new OCT images

2. **See Results**
   - Top prediction with confidence
   - All 16 predictions ranked
   - Color-coded confidence bars

3. **Export Results**
   - Screenshot predictions
   - Save results as image
   - (Advanced: Add export button)

## 🔧 Customization Ideas

### Add More Features

```javascript
// In src/App.js
- Download results as CSV
- Save prediction history
- Batch process multiple images
- Real-time accuracy stats
```

### Change Styling

```css
/* In src/App.css */
- Change colors (purple → blue/red/green)
- Adjust layout (sidebar, full-width)
- Add animations
- Mobile optimizations
```

### Backend Enhancements

```python
# In api_server.py
- Add image logging
- Add user authentication
- Add database for history
- Add model versioning
```

## 🚢 Deployment Options

After building (`npm run build`):

### Option 1: Local Network

```bash
npm run build
npm install -g serve
serve -s build
```

Access from other machines: `http://your-machine-ip:3000`

### Option 2: Docker

Create Dockerfile for containerized deployment

### Option 3: Cloud Services

- Vercel (React frontend)
- AWS Lambda (Flask backend)
- Heroku (full stack)
- DigitalOcean (VPS)

## 📈 Next Steps After Setup

1. ✅ Verify everything works with test images
2. ✅ Test with all 16 categories
3. ✅ Change colors/styling if desired
4. ✅ Add more features as needed
5. ✅ Deploy to production
6. ✅ Monitor and improve

## ❓ Common Questions

**Q: Can I close the backend terminal?**
A: No, keep both terminals open. The app won't work if one closes.

**Q: Will it work on my phone?**
A: If on same network, yes! Use your computer's IP address.

**Q: How do I make predictions faster?**
A: Enable GPU with CUDA PyTorch installation.

**Q: Can I use my own model?**
A: Yes, replace final_model.pth with your trained model.

---

## ✅ Success Checklist

When everything is working, you should have:

- ✅ Terminal 1 showing "🚀 Starting Flask server"
- ✅ Terminal 2 showing "webpack compiled successfully"
- ✅ Browser at http://localhost:3000
- ✅ Purple header with upload area
- ✅ Can upload images and see predictions
- ✅ Results show confidence percentages

## 🎉 Ready to Go!

Follow the 6 steps above and you'll have a fully functional OCT classification web application!

**Questions? Check REACT_SETUP.md for detailed documentation.**

---

**Happy classifying! 🏥🔬**
