# ComfyUI + Kaggle GPU Integration Project

## Overview
A complete setup for running ComfyUI on a normal laptop without local GPU by integrating with Kaggle for GPU resources and GitHub for model/config storage.

## Quick Start

### 1. Install Dependencies
```bash
# Install CPU-only PyTorch (no GPU needed)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install project dependencies
pip install kaggle pandas numpy gitpython huggingface-hub safetensors tqdm psutil comfyui
```

### 2. Setup Kaggle Credentials
1. Go to https://www.kaggle.com/account?tab=apikeys
2. Create API tokens and save `kaggle.json` to `~/.kaggle/`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Test: `kaggle --version`

### 3. Download Models
```bash
python scripts/download_models.py
```

### 4. Launch ComfyUI
```bash
python scripts/launch_comfyui.py
```

Open `http://localhost:8188` in your browser!

## Project Structure
```
/comfyui_project/
├── models/
│   ├── stable_diffusion/    # Downloaded SD models
│   ├── control_nets/        # ControlNet models
│   └── custom/             # Custom/fine-tuned models
├── workflows/               # ComfyUI workflow JSON files
│   ├── text_to_image.json    # Basic text-to-image
│   ├── control_net_workflow.json  # ControlNet guided
│   └── custom_model_workflow.json # Custom models
├── scripts/                 # Automation scripts
│   ├── download_models.py    # Download SD/ControlNet models
│   ├── kaggle_sync.py       # Sync with Kaggle
│   ├── storage_monitor.py   # Monitor storage
│   └── launch_comfyui.py    # Launch ComfyUI
├── outputs/
│   ├── generated/          # Generated images
│   └── temporary/          # Cache files
└── documentation/          # Setup guides
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Kaggle GPU Access** | Use Kaggle's free GPUs when needed |
| **GitHub Integration** | Version control for workflows and configs |
| **Model Management** | Built for 50-100GB storage |
| **Automation** | Scripts for downloads, sync, monitoring |
| **Stable Diffusion** | SD v1.5, SD v2.1, SDXL, upscalers |
| **ControlNet** | v1.1, v1.2, v1.3, v1.4 |

## Model Downloads

SD Models:
- `runwayml/stable-diffusion-v1-5`
- `stabilityai/stable-diffusion-2-1`
- `stabilityai/stable-diffusion-xl-base-1.0`

ControlNet Models:
- `lllyasviel/ControlNet-v1-1`
- `lllyasviel/ControlNet-v1-2`
- `lllyasviel/ControlNet-v1-3`

## Documentation

- `comfyui_kaggle_setup_roadmap.md` - Complete 10-phase setup guide
- `documentation/setup_guide.md` - Detailed step-by-step instructions
- `essentials.txt` - Quick reference commands

## Storage

Recommended: 50GB+ free space

| Directory | Appx. Size |
|-----------|------------|
| Models | ~30GB |
| Generated Results | ~20GB |
| Temp/Cache | ~5GB |

## Troubleshooting

**Port 8188 in use:**
```bash
python scripts/launch_comfyui.py --port 8189
```

**Models not found:**
```bash
python scripts/launch_comfyui.py --check-only
```

**Kaggle auth error:**
```bash
ls -la ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

## License
Open source - feel free to contribute and improve!

---

*Last updated: November 24, 2026*