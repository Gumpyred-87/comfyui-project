# ComfyUI + Kaggle Setup Guide

## Quick Start (3 Steps)

### 1. Clone and Setup Repository
```bash
git clone https://github.com/yourusername/comfyui-kaggle-project.git
cd comfyui-kaggle-project
python scripts/download_models.py
```

### 2. Configure Kaggle
1. Get Kaggle API credentials from https://www.kaggle.com/account?tab=apikeys
2. Save `kaggle.json` to `~/.kaggle/`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Test with: `kaggle --version`

### 3. Launch ComfyUI
```bash
python scripts/launch_comfyui.py
```

Open `http://localhost:8188` in your browser and start creating!

## Step-by-Step Setup

### Phase 1: Initial Setup

#### 1.1 Clone Repository
```bash
# Replace with your GitHub username
 git clone https://github.com/yourusername/comfyui-kaggle-project.git
 cd comfyui-kaggle-project
```

#### 1.2 Install Python Dependencies
```bash
# Install CPU-only PyTorch (no GPU needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install project dependencies
pip install kaggle pandas numpy gitpython huggingface-hub safetensors tqdm psutil

# Install ComfyUI
pip install comfyui
```

#### 1.3 Setup Directory Structure
```
/comfyui_project/
├── models/
│   ├── stable_diffusion/    # Downloaded SD models
│   ├── control_nets/        # ControlNet models
│   └── custom/             # Your custom models
├── workflows/               # ComfyUI workflow files
├── scripts/                 # Automation scripts
├── outputs/                 # Generated images
│   ├── generated/          # Your created images
│   └── temporary/          # Cache files
└── documentation/          # This guide
```

### Phase 2: Model Setup

#### 2.1 Download Models
```bash
python scripts/download_models.py
```

This downloads:
- **Stable Diffusion models**: SD v1.5, SD v2.1, SDXL, upscalers
- **ControlNet models**: v1.1, v1.2, v1.3, v1.4
- **Custom model structure**: For your Kaggle models

#### 2.2 Check Model Availability
```bash
# Quick check
python -c "from pathlib import Path; print('Models available:', any(Path('models').iterdir()))"

# Detailed check
python scripts/launch_comfyui.py --check-only
```

### Phase 3: Kaggle Integration Setup

#### 3.1 Install Kaggle CLI
```bash
# If not already installed
pip install kaggle

# Create .kaggle directory
mkdir -p ~/.kaggle

# Upload kaggle.json (from Kaggle.com)
chmod 600 ~/.kaggle/kaggle.json
```

#### 3.2 Test Kaggle Connection
```bash
kaggle --version
kaggle datasets list
```

#### 3.3 Sync Custom Models (Optional)
```bash
# Sync custom models from your Kaggle datasets
python scripts/kaggle_sync.py --mode custom

# Sync outputs back to Kaggle
python scripts/kaggle_sync.py --mode outputs

# Sync models to Kaggle (for sharing)
python scripts/kaggle_sync.py --mode models
```

### Phase 4: ComfyUI Usage

#### 4.1 Launch ComfyUI
```bash
# Basic launch
python scripts/launch_comfyui.py

# Or use ComfyUI directly
python -m comfyui
```

#### 4.2 Import Workflows
In ComfyUI web interface (`http://localhost:8188`):

1. Click "Workflow" → "Load" in the top menu
2. Select workflow files from `workflows/` directory:
   - `text_to_image.json` - Basic text-to-image
   - `control_net_workflow.json` - Image-conditioned generation

#### 4.3 Create Your First Image
1. Load `text_to_image.json` workflow
2. Set your prompt in the "Prompt" node
3. Adjust parameters as needed
4. Click "Execute" to generate

### Phase 5: Storage Management

#### 5.1 Monitor Storage
```bash
# Generate comprehensive storage report
python scripts/storage_monitor.py

# Check storage usage
python -c "
import subprocess
result = subprocess.run(['python', 'scripts/storage_monitor.py'], 
                       capture_output=True, text=True)
print(result.stdout)
"
```

#### 5.2 Cleanup Scripts
```bash
# Manual cleanup when needed
rm -rf outputs/temporary/*

# Automated cleanup (add to cron job)
# Run daily at 2 AM
0 2 * * * cd /path/to/comfyui_project && python scripts/storage_monitor.py --report-only
```

### Phase 6: Git Integration

#### 6.1 Track Changes
```bash
# Stage workflow changes
git add workflows/

# Stage model updates (if any)
git add models/custom/

# Commit with descriptive message
git commit -m "Add new workflow and update custom model"

# Push to GitHub (if you have write access)
git push origin main
```

#### 6.2 Best Practices
- Don't commit large model files to git
- Use `.gitignore` to exclude temporary files
- Version control your workflows and configurations
- Archive completed projects regularly

## Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named comfyui"
**Solution:** Install ComfyUI
```bash
pip install comfyui
```

#### Issue: Kaggle authentication fails
**Solution:** Check credentials
```bash
# Verify kaggle.json exists and has correct format
ls -la ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
kaggle --version
```

#### Issue: Port 8188 is already in use
**Solution:** Use different port or stop existing service
```bash
# Try alternative ports
python scripts/launch_comfyui.py --port 8189

# Or stop existing ComfyUI
python scripts/launch_comfyui.py --stop
```

#### Issue: Models take too long to download
**Solution:** Check internet connection and try again
```bash
# Resume interrupted downloads
python scripts/download_models.py
```

### System Requirements Check

#### Minimum Requirements
- **OS:** Windows 10/11 or equivalent
- **RAM:** 8GB minimum (16GB recommended for faster loading)
- **Storage:** 50GB free space
- **Python:** 3.7 or higher

#### Recommended for Better Performance
- **RAM:** 16GB or more
- **Storage:** SSD with at least 100GB free
- **GPU:** Any GPU (for CPU-only setup, use Kaggle GPU)

## Advanced Features

### 1. Kaggle GPU Integration
Use Kaggle notebooks for GPU-intensive tasks:
```python
# Example Kaggle notebook code
import torch
from diffusers import StableDiffusionPipeline

# Load model on GPU
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
)
pipe = pipe.to("cuda")

# Generate image
image = pipe("beautiful landscape").images[0]
```

### 2. Custom Model Training
Train your own models on Kaggle:
1. Upload dataset to Kaggle
2. Use Kaggle GPU for training
3. Download trained models back to local

### 3. Automated Workflows
Create automated pipelines:
```python
# Example automation script
from scripts.kaggle_sync import KaggleSynchronizer
from scripts.storage_monitor import StorageMonitor

synchronizer = KaggleSynchronizer(".")
storage_monitor = StorageMonitor(".")

# Run nightly sync
if datetime.now().hour == 2:  # 2 AM
    synchronizer.run_full_sync("all")

# Check storage
storage_monitor.generate_comprehensive_report()
```

### 4. Web Interface Customization
Create custom web interface for easier workflow management:
1. Use Streamlit or Gradio
2. Integrate with ComfyUI API
3. Add model selection UI
4. Track generation history

## Support and Community

### Resources
- **ComfyUI Documentation:** https://github.com/comfyanonymous/ComfyUI
- **Kaggle Documentation:** https://www.kaggle.com/docs
- **GitHub Repository:** https://github.com/yourusername/comfyui-kaggle-project
- **Issues:** https://github.com/yourusername/comfyui-kaggle-project/issues

### Getting Help
1. Check the [README.md](README.md) for basic setup
2. Review the [setup_guide.md](documentation/setup_guide.md) for detailed instructions
3. Check the [comfyui_kaggle_setup_roadmap.md](comfyui_kaggle_setup_roadmap.md) for complete roadmap
4. Join the ComfyUI community for support

## Project Maintenance

### Regular Tasks
- **Monthly:** Clean temporary files, check for large files
- **Quarterly:** Update dependencies, review workflows
- **Semi-annually:** Archive old projects, backup important models

### Backup Strategy
1. **Daily backups:** Git commits for code and configs
2. **Weekly backups:** Archive completed projects
3. **Monthly backups:** Full system backup if possible

This setup guide provides everything you need to start using ComfyUI with Kaggle integration for GPU access on a normal laptop. The system is designed to be:

- **Scalable:** Add more models and workflows as needed
- **Maintainable:** Automated scripts for updates and monitoring
- **Flexible:** Easy to integrate with existing workflows
- **Robust:** Comprehensive error handling and troubleshooting

Enjoy creating with ComfyUI! 🎨✨

---

*Last updated: November 24, 2026*
*Version: 1.0*