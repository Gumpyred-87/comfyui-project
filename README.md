# ComfyUI + Kaggle GPU Integration Project

## Overview
A complete setup for running ComfyUI on a normal laptop without local GPU by integrating with Kaggle for GPU resources and GitHub for model/config storage.

## Project Structure
```
/comfyui_project/
├── models/
│   ├── stable_diffusion/    # Base SD models
│   ├── control_nets/        # ControlNet models
│   └── custom/             # User-trained/custom models
├── configs/                 # Configuration files
│   ├── comfyui/            # ComfyUI workflows and settings
│   └── model_configs/      # Model-specific configs
├── scripts/                 # Automation scripts
│   ├── download_models.py  # Download and manage models
│   ├── kaggle_sync.py      # Sync with Kaggle
│   └── storage_monitor.py  # Monitor storage usage
├── ComfyUI/                 # ComfyUI installation
│   ├── user/
│   │   └── default/
│   │       └── workflows/  # Workflow files
│   └── environment.py      # Environment setup
├── outputs/
│   ├── generated/          # Generated images
│   └── temporary/          # Cache files
└── documentation/          # Project documentation
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/comfyui-kaggle-project.git
cd comfyui-kaggle-project
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install kaggle pandas numpy gitpython huggingface-hub safetensors

# Install ComfyUI
pip install comfyui
```

### 3. Setup Kaggle API
1. Download `kaggle.json` from Kaggle.com
2. Move it to `~/.kaggle/`
3. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Test: `kaggle --version`

### 4. Download Initial Models
```bash
python scripts/download_models.py
```

### 5. Launch ComfyUI
```bash
python -m comfyui
```

Open browser to `http://localhost:8188`

## Key Scripts

### download_models.py
Downloads and manages all required models for ComfyUI:
- Stable Diffusion models (SD v1.5, SD v2.1, upscalers)
- ControlNet models (v1.1, v1.2, v1.3)
- Hugging Face integration

### kaggle_sync.py
Synchronizes models and datasets between Kaggle and local storage:
- Downloads custom models from Kaggle
- Uploads generated outputs to Kaggle
- Manages version control

### storage_monitor.py
Monitors and manages storage usage:
- Tracks model, output, and config sizes
- Checks available disk space
- Recommends cleanup actions

## Configuration

### ComfyUI Workflows
All workflow files are in `ComfyUI/user/default/workflows/`:
- `text_to_image.json`: Basic text-to-image generation
- `control_net_workflow.json`: ControlNet-based workflows
- `custom_model_workflow.json`: Workflows for custom models

### Environment Variables
Create `.env` file in project root:
```bash
MODEL_DIR=models/stable_diffusion
CONTROLNET_DIR=models/control_nets
CUSTOM_DIR=models/custom
OUTPUT_DIR=outputs/generated
TEMP_DIR=outputs/temporary
```

## Usage Examples

### Text-to-Image Generation
1. Load `text_to_image.json` workflow in ComfyUI
2. Set prompt and parameters
3. Click "Execute" to generate images
4. Outputs saved to `outputs/generated/`

### ControlNet Workflow
1. Load `control_net_workflow.json` workflow
2. Upload control image (pose, depth, etc.)
3. Set prompt and guidance scale
4. Generate images with control

### Custom Model Usage
1. Place custom models in `models/custom/`
2. Update workflow JSON to reference custom models
3. Use custom workflows for specialized tasks

## Git Workflow

### Basic Commands
```bash
# Check status
git status

# Stage changes
git add outputs/ configs/ models/custom/

# Commit with descriptive message
git commit -m "Generate images using workflow X"

# Push to remote (if you have write access)
git push origin main
```

### Best Practices
- Use `.gitignore` to exclude large files:
  ```
  *.safetensors
  models/stable_diffusion/*/cache*
  outputs/temporary/*
  ```

- Commit only workflow and config changes
- Archive generated outputs periodically
- Use tags for major releases

## Storage Management

### Recommended Structure
```
outputs/
├── generated/
│   ├── 2024/        # Generated images (organized by date)
│   ├── 2025/
│   └── 2026/
└── temporary/      # Cache and temporary files
```

### Storage Monitoring
```bash
python scripts/storage_monitor.py
```

### Cleanup Commands
```bash
# Remove temporary files
rm -rf outputs/temporary/*

# Archive old outputs (example script)
./scripts/archive_outputs.sh
```

## Troubleshooting

### Common Issues

**Kaggle API Errors**
```bash
# Check configuration
kaggle datasets list

# Verify authentication
ls -la ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

**Model Download Issues**
```bash
# Check if directories exist
ls -la models/stable_diffusion/
ls -la models/control_nets/

# Re-download if needed
python scripts/download_models.py
```

**Storage Full**
```bash
# Check usage
python scripts/storage_monitor.py

# Clean temporary files
rm -rf outputs/temporary/*

# Archive old outputs
mkdir -p outputs/archive/$(date +%Y-%m-%d)
mv outputs/generated/*/* outputs/archive/$(date +%Y-%m-%d)/
```

## Future Enhancements

### GPU Integration (When Available)
1. Update PyTorch for CUDA support
2. Set `CUDA_VISIBLE_DEVICES` environment variable
3. Configure ComfyUI for GPU acceleration
4. Implement distributed training using Kaggle

### Additional Features
1. **Model Fine-tuning**: Use Kaggle for custom model training
2. **Version Control**: Track model versions and configurations
3. **CI/CD Pipeline**: Automate testing and deployment
4. **Web Interface**: Custom web UI for easier interaction

## Getting Help

- Check the full roadmap in `comfyui_kaggle_setup_roadmap.md`
- Join the ComfyUI community forums
- Use Kaggle documentation for GPU resources
- Check GitHub issues for known problems

## License
This project is open source. Feel free to contribute and improve!
```