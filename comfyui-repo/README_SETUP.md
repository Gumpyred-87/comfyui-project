# ComfyUI + Kaggle - Setup Summary

## 🚀 Quick Commands for Your Laptop

Clone this repo first:
```bash
git clone https://github.com/Gumpyred-87/comfyui-project.git
cd comfyui-project
```

### Step 1: Install Dependencies
```bash
# Windows:
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install kaggle pandas numpy gitpython huggingface-hub safetensors tqdm psutil comfyui

# macOS/Linux:
pip3 install --upgrade pip
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install kaggle pandas numpy gitpython huggingface-hub safetensors tqdm psutil comfyui
```

### Step 2: Setup Kaggle API
1. Go to https://www.kaggle.com/account?tab=apikeys
2. Click "New Token" to get API credentials
3. Download `kaggle.json` to your computer
4. Move `kaggle.json` to: `~/.kaggle/` (Windows: `C:\Users\Your_Name\.kaggle\`)
5. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

### Step 3: Download Models
```bash
python scripts/download_models.py
```

This downloads:
- Stable Diffusion models (SD v1.5, SD v2.1, SDXL)
- ControlNet models (v1.1-v1.4)

### Step 4: Launch ComfyUI
```bash
python scripts/launch_comfyui.py
```

Open `http://localhost:8188` in your browser - you're ready!

---

## 📊 Project Structure
```
/comfyui_project/
├── models/              # Downloaded models (~30GB)
│   ├── stable_diffusion/
│   ├── control_nets/
│   └── custom/
├── workflows/           # ComfyUI workflow JSONs
├── scripts/             # Automation scripts
├── outputs/             # Generated images
└── documentation/       # Guides
```

---

## 📋 Key Files
| File | What It Does |
|------|--------------|
| `scripts/download_models.py` | Downloads all models |
| `scripts/kaggle_sync.py` | Syncs with Kaggle |
| `scripts/storage_monitor.py` | Monitors storage |
| `scripts/launch_comfyui.py` | Launches ComfyUI |
| `workflows/text_to_image.json` | Basic SD workflow |
| `workflows/control_net_workflow.json` | ControlNet workflow |

---

## 🎨 Workflows in ComfyUI
1. Go to `http://localhost:8188`
2. Click "Workflow" → "Load"
3. Select `workflows/text_to_image.json` or `workflows/control_net_workflow.json`
4. Edit prompt, click "Execute"

---

## ⚡ Key Features
- ✅ **Kaggle GPU Access** - Use free GPUs when needed
- ✅ **GitHub Integration** - Version control
- ✅ **50-100GB storage ready** - For SD models and outputs
- ✅ **CPU-based** - Works on normal laptops

---

## 🛠️ Troubleshooting

**Port 8188 in use:**
```bash
python scripts/launch_comfyui.py --port 8189
```

**Models missing:**
```bash
python scripts/launch_comfyui.py --check-only
```

**Kaggle auth error:**
```bash
ls -la ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

**Low storage:**
```bash
python scripts/storage_monitor.py
```

---

## 📁 Repository Links
- Repository: `https://github.com/Gumpyred-87/comfyui-project`
- Issues: Open an issue on GitHub if you need help

---

## 💡 Tips
- Don't commit large model files to git! (.safetensors)
- Use GitHub Releases for sharing models
- Check `comfyui_kaggle_setup_roadmap.md` for complete setup guide

---

*Last updated: November 24, 2026*