# ComfyUI + Kaggle GPU Integration Setup Roadmap

## Overview
Set up ComfyUI on a normal laptop without local GPU access by integrating with Kaggle for GPU resources and GitHub for model/config storage.

## Prerequisites
- Windows 11 laptop
- Kaggle account with API credentials
- GitHub account with repositories
- 50-100GB storage space available
- ComfyUI installation (will be set up)

## Phase 1: Environment Setup

### 1.1 Install ComfyUI
```bash
# Clone ComfyUI from GitHub
git clone https://github.com/comfyanonymous/ComfyUI.git

# Navigate to the directory
cd ComfyUI

# Create a virtual environment (recommended)
python -m venv comfyui_env
source comfyui_env/bin/activate  # Windows: comfyui_env\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt  # If available
```

### 1.2 Install Additional Dependencies
```bash
# For Kaggle integration
pip install kaggle pandas numpy

# For GitHub integration
pip install gitpython

# For model management
pip install huggingface-hub safetensors
```

### 1.3 Kaggle API Setup
1. Go to Kaggle.com → Account → Create API credentials
2. Save `kaggle.json` to `~/.kaggle/`
3. Set proper permissions: `chmod 600 ~/.kaggle/kaggle.json`
4. Test installation: `kaggle --version`

## Phase 2: GitHub Repository Setup

### 2.1 Create Organization Structure
```
/comfyui_project/
├── models/
│   ├── stable_diffusion/
│   ├── control_nets/
│   └── custom/
├── configs/
│   ├── comfyui/
│   └── model_configs/
├── scripts/
│   ├── download_models.py
│   └── kaggle_sync.py
├── outputs/
│   ├── generated/
│   └── temporary/
└── documentation/
```

### 2.2 Initialize Git Repository
```bash
cd /path/to/comfyui_project
git init
git config user.name "Your Name"
git config user.email "your.email@gmail.com"
```

## Phase 3: Kaggle GPU Integration

### 3.1 Create GPU Runtime Scripts
**download_models.py**
```python
import kaggle
import os
import shutil
from huggingface_hub import snapshot_download

def download_from_kaggle(dataset_id, dest_path):
    """Download models/datasets from Kaggle"""
    print(f"Downloading {dataset_id} to {dest_path}")
    kaggle.api.datasets_download(dataset_id, path=dest_path)

def download_from_huggingface(model_id, dest_path):
    """Download models from Hugging Face"""
    print(f"Downloading {model_id} to {dest_path}")
    snapshot_download(repo_id=model_id, local_dir=dest_path)

if __name__ == "__main__":
    # Example downloads
    os.makedirs("models/stable_diffusion", exist_ok=True)
    download_from_huggingface("runwayml/stable-diffusion-v1-5", "models/stable_diffusion")
    
    os.makedirs("models/control_nets", exist_ok=True)
    download_from_huggingface("lllyasviel/ControlNet-v1-1", "models/control_nets")
```

**kaggle_sync.py**
```python
import kaggle
import json
import os
from pathlib import Path

def sync_kaggle_model(model_name, local_dir):
    """Sync model from Kaggle to local storage"""
    try:
        kaggle.api.dataset_download_files(
            model_name,
            path=local_dir,
            force=False
        )
        print(f"Successfully synced {model_name}")
    except Exception as e:
        print(f"Error syncing {model_name}: {e}")

if __name__ == "__main__":
    # Create directories
    Path("models/custom").mkdir(parents=True, exist_ok=True)
    
    # Sync custom models from Kaggle
    sync_kaggle_model("username/model-dataset", "models/custom")
```

### 3.2 GPU Access Setup
1. **Kaggle Kernel Setup**: Use Kaggle notebooks for GPU-intensive tasks
2. **Remote Execution**: Queue jobs to Kaggle's GPU resources
3. **Model Fine-tuning**: Use Kaggle for training, download results locally

## Phase 4: ComfyUI Configuration

### 4.1 Basic ComfyUI Setup
Create `ComfyUI/user/default/workflows/` directory:
```
/comfyui_project/
└── ComfyUI/
    └── user/
        └── default/
            └── workflows/
                ├── text_to_image.json
                ├── control_net_workflow.json
                └── custom_model_workflow.json
```

### 4.2 Workflow Files
**text_to_image.json** (basic Stable Diffusion workflow)
```json
{
    "name": "Text to Image",
    "nodes": [
        {
            "name": "Prompt",
            "type": "CLIPTextEncode",
            "params": {
                "text": "your prompt here"
            }
        },
        {
            "name": "Sampler",
            "type": "KSampler",
            "params": {
                "seed": 42,
                "steps": 20,
                "cfg": 7.5
            }
        }
    ]
}
```

**control_net_workflow.json**
```json
{
    "name": "ControlNet Workflow",
    "nodes": [
        {
            "name": "ControlNet Load",
            "type": "ControlNet",
            "params": {
                "model_path": "models/control_nets/controlnet-v1-1.safetensors"
            }
        }
    ]
}
```

### 4.3 ComfyUI Environment Variables
Create `.env` file:
```bash
# Model paths
MODEL_DIR=models/stable_diffusion
CONTROLNET_DIR=models/control_nets
CUSTOM_DIR=models/custom

# Output directories
OUTPUT_DIR=outputs/generated
TEMP_DIR=outputs/temporary

# GPU settings (for future GPU integration)
CUDA_VISIBLE_DEVICES=0  # Will be managed by Kaggle integration
```

## Phase 5: Model Management

### 5.1 Initial Model Downloads
**download_script.py**
```python
import os
from pathlib import Path
from huggingface_hub import snapshot_download

def download_stable_diffusion():
    """Download Stable Diffusion models"""
    models_to_download = [
        ("runwayml/stable-diffusion-v1-5", "sd_v1_5"),
        ("stabilityai/stable-diffusion-2-1", "sd_v2_1"),
        ("runwayml/stable-diffusion-v1-5-upscaler", "sd_upscaler")
    ]
    
    for model_id, subdir in models_to_download:
        dest = Path("models/stable_diffusion") / subdir
        dest.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {model_id} to {dest}")
        snapshot_download(repo_id=model_id, local_dir=str(dest))

def download_control_nets():
    """Download ControlNet models"""
    models_to_download = [
        ("lllyasviel/ControlNet-v1-1", "controlnet_v1_1"),
        ("lllyasviel/ControlNet-v1-2", "controlnet_v1_2"),
        ("lllyasviel/ControlNet-v1-3", "controlnet_v1_3")
    ]
    
    for model_id, subdir in models_to_download:
        dest = Path("models/control_nets") / subdir
        dest.mkdir(parents=True, exist_ok=True)
        print(f"Downloading {model_id} to {dest}")
        snapshot_download(repo_id=model_id, local_dir=str(dest))

if __name__ == "__main__":
    os.makedirs("models/stable_diffusion", exist_ok=True)
    os.makedirs("models/control_nets", exist_ok=True)
    
    print("Starting model downloads...")
    download_stable_diffusion()
    download_control_nets()
    print("Model downloads complete!")
```

### 5.2 Git Integration for Models
```bash
# Add models to git (use .gitignore for large model files)
echo "*.safetensors" >> .gitignore
echo "models/stable_diffusion/*/cache*" >> .gitignore

echo "Adding models to git..."
git add models/
git commit -m "Add initial model set"
```

## Phase 6: Storage Management

### 6.1 Directory Structure
```
/comfyui_project/
├── models/
│   ├── stable_diffusion/
│   │   ├── sd_v1_5/
│   │   ├── sd_v2_1/
│   │   └── sd_upscaler/
│   ├── control_nets/
│   │   ├── controlnet_v1_1/
│   │   ├── controlnet_v1_2/
│   │   └── controlnet_v1_3/
│   └── custom/
├── outputs/
│   ├── generated/
│   │   ├── 2024/
│   │   ├── 2025/
│   │   └── 2026/
│   └── temporary/  # Cache files
├── configs/
│   ├── comfyui/
│   └── model_configs/
└── scripts/
    ├── download_models.py
    ├── kaggle_sync.py
    └── comfyui_setup.py
```

### 6.2 Storage Monitoring
**storage_monitor.py**
```python
import os
import shutil
from pathlib import Path

def get_directory_size(path):
    """Get total size of directory in GB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass
    return total_size / (1024**3)  # Convert to GB

def monitor_storage():
    """Monitor storage usage"""
    directories = {
        "Models": "models/",
        "Outputs": "outputs/generated",
        "Configs": "configs/"
    }
    
    print("Storage Usage Monitor:")
    print("-" * 40)
    
    for name, path in directories.items():
        if os.path.exists(path):
            size = get_directory_size(path)
            print(f"{name}: {size:.2f} GB")
        else:
            print(f"{name}: Not found")
    
    # Check available space
    drive = os.path.splitdrive(os.getcwd())[0]
    total, used, free = shutil.disk_usage(drive)
    print(f"\nAvailable space on {drive}:")
    print(f"Free: {free / (1024**3):.2f} GB")
    print(f"Used: {used / (1024**3):.2f} GB")

if __name__ == "__main__":
    monitor_storage()
```

## Phase 7: Workflow Automation

### 7.1 ComfyUI Launcher Script
**launch_comfyui.py**
```python
import subprocess
import os
import time
from pathlib import Path

def launch_comfyui():
    """Launch ComfyUI with proper environment"""
    # Set up environment
    env = os.environ.copy()
    env['COMFYUI_ROOT'] = str(Path.cwd() / 'ComfyUI')
    env['MODEL_DIR'] = str(Path.cwd() / 'models/stable_diffusion')
    env['CONTROLNET_DIR'] = str(Path.cwd() / 'models/control_nets')
    
    # Launch ComfyUI
    cmd = [
        'python', '-m', 'comfyui',
        '--port', '8188'
    ]
    
    print("Launching ComfyUI...")
    print(f"Model directory: {env['MODEL_DIR']}")
    print(f"ControlNet directory: {env['CONTROLNET_DIR']}")
    
    # Run ComfyUI
    subprocess.run(cmd, env=env)

if __name__ == "__main__":
    launch_comfyui()
```

### 7.2 Kaggle Integration Script
**kaggle_gpu_workflow.py**
```python
import kaggle
import subprocess
import os
from pathlib import Path

def prepare_kaggle_job(model_name, input_data, output_path):
    """Prepare a job for Kaggle GPU processing"""
    # Save input data locally
    input_file = Path("inputs") / f"{model_name}_input.json"
    input_file.parent.mkdir(exist_ok=True)
    
    import json
    with open(input_file, 'w') as f:
        json.dump(input_data, f)
    
    # Create Kaggle notebook script
    notebook_script = f"""
import pandas as pd
import torch
import os
from pathlib import Path

# Load model
model_path = "models/stable_diffusion/{model_name}"
# Your model loading code here

# Process input data
input_data = pd.read_json("{input_file}")

# Generate outputs
# Your generation code here

# Save output
output_path = "{output_path}"
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
# Save your outputs
"""
    
    return input_file, notebook_script

def run_kaggle_gpu(notebook_script, input_file):
    """Execute GPU-intensive tasks on Kaggle"""
    # Use kaggle api to run notebook
    kaggle.api.kernels_push(
        kernel_name="comfyui-gpu-workflow",
        code=notebook_script,
        data_files=[str(input_file)]
    )

def download_kaggle_results(output_id, local_path):
    """Download results from Kaggle"""
    kaggle.api.dataset_download_files(
        output_id,
        path=local_path,
        force=True
    )

if __name__ == "__main__":
    # Example usage
    model_name = "custom-model"
    input_data = {
        "prompts": ["A beautiful landscape", "A futuristic city"],
        "parameters": {"seed": 42, "steps": 20}
    }
    output_path = "outputs/generated/kaggle_results"
    
    print("Preparing Kaggle GPU job...")
    input_file, notebook_script = prepare_kaggle_job(
        model_name, input_data, output_path
    )
    
    print("Running on Kaggle GPU...")
    run_kaggle_gpu(notebook_script, input_file)
    
    print("Downloading results...")
    download_kaggle_results("username/output-dataset", output_path)
```

## Phase 8: Usage Workflow

### 8.1 Basic Usage Commands
```bash
# Download initial models
python scripts/download_models.py

# Sync with Kaggle
python scripts/kaggle_sync.py

# Launch ComfyUI
python scripts/launch_comfyui.py

# Monitor storage
python scripts/storage_monitor.py

# Create workflow
# 1. Open ComfyUI web interface at http://localhost:8188
# 2. Load your workflow JSON files
# 3. Customize parameters in the workflow
# 4. Generate images!
```

### 8.2 Git Workflow
```bash
# Check git status
git status

# Stage changes
git add outputs/ configs/

# Commit changes with descriptive message
git commit -m "Generate images using custom workflow"

# Push to GitHub (if you have write access)
git push origin main
```

### 8.3 Backup Strategy
```bash
# Create weekly backup script
bash scripts/backup_weekly.sh

# Create daily cache cleanup script
bash scripts/cleanup_cache.sh
```

## Phase 9: Troubleshooting

### 9.1 Common Issues and Solutions

**Issue: Kaggle authentication fails**
```bash
# Check if kaggle.json is in correct location
ls -la ~/.kaggle/kaggle.json
# Set proper permissions
chmod 600 ~/.kaggle/kaggle.json
# Test connection
kaggle datasets list
```

**Issue: Storage space is full**
```bash
# Check storage usage
python scripts/storage_monitor.py

# Clean temporary files
rm -rf outputs/temporary/*

# Archive old outputs
mkdir -p outputs/archive/$(date +%Y-%m-%d)
mv outputs/generated/*/* 2024-*/outputs/archive/$(date +%Y-%m-%d)/
```

**Issue: ComfyUI cannot find models**
```bash
# Verify model directories exist
ls -la models/stable_diffusion/
ls -la models/control_nets/

# Re-download if necessary
python scripts/download_models.py
```

## Phase 10: Performance Optimization

### 10.1 For Normal Laptop Performance
1. **Use CPU-only PyTorch**: Already configured in setup
2. **Limit concurrent processes**: Monitor system resources
3. **Pre-download models**: Use scripts for offline access
4. **Use efficient workflows**: Optimize ComfyUI node configurations

### 10.2 Future GPU Integration
When you get GPU access:
1. Update PyTorch install: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`
2. Set `CUDA_VISIBLE_DEVICES` environment variable
3. Update ComfyUI configuration for GPU acceleration
4. Implement distributed training using Kaggle

## Summary

This roadmap provides a complete setup for running ComfyUI on a normal laptop without local GPU by:

1. **Setting up ComfyUI** with CPU-compatible dependencies
2. **Integrating Kaggle** for GPU resources and model storage
3. **Organizing GitHub repositories** for model and config management
4. **Creating automation scripts** for downloads and workflows
5. **Setting up storage management** for 50-100GB of data
6. **Providing troubleshooting guides** for common issues

The system is designed to be:
- **Scalable**: Add more models as storage allows
- **Maintainable**: Automated downloads and backups
- **Flexible**: Easy to integrate with future GPU access
- **Reproducible**: Git-based version control

You can start with Phase 1-2 immediately and continue with subsequent phases as needed.
```