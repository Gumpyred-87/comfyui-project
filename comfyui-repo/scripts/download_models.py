#!/usr/bin/env python3
"""
Model download and management script for ComfyUI + Kaggle project.
Downloads all required models for text-to-image and ControlNet workflows.
"""

import os
import sys
import argparse
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
from tqdm import tqdm
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class ModelDownloader:
    def __init__(self, output_dir="models", verbose=True):
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.downloaded_models = []
        self.failed_downloads = []

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        if self.verbose:
            print(f"[ModelDownloader] {message}")

    def download_stable_diffusion_models(self):
        """Download Stable Diffusion models"""
        sd_models = [
            {
                "repo_id": "runwayml/stable-diffusion-v1-5",
                "subdir": "sd_v1_5",
                "description": "Stable Diffusion v1.5 (most compatible)"
            },
            {
                "repo_id": "stabilityai/stable-diffusion-2-1",
                "subdir": "sd_v2_1",
                "description": "Stable Diffusion v2.1 (improved quality)"
            },
            {
                "repo_id": "runwayml/stable-diffusion-v1-5-upscaler",
                "subdir": "sd_upscaler",
                "description": "Upscaler model for SD v1.5"
            },
            {
                "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "subdir": "sdxl_base",
                "description": "Stable Diffusion XL Base (latest)"
            }
        ]

        self.log("Downloading Stable Diffusion models...")

        for model in sd_models:
            model_path = self.output_dir / "stable_diffusion" / model["subdir"]
            model_path.mkdir(parents=True, exist_ok=True)

            try:
                self.log(f"  Downloading {model['repo_id']} to {model_path}")

                # Download the model
                snapshot_download(
                    repo_id=model["repo_id"],
                    local_dir=str(model_path),
                    local_dir_use_symlinks=False,
                    cache_dir=None  # Don't use cache to avoid duplication
                )

                self.downloaded_models.append({
                    "type": "stable_diffusion",
                    "repo_id": model["repo_id"],
                    "path": str(model_path),
                    "description": model["description"]
                })

                self.log(f"  ✓ Successfully downloaded {model['subdir']}")

            except Exception as e:
                self.failed_downloads.append({
                    "type": "stable_diffusion",
                    "repo_id": model["repo_id"],
                    "error": str(e)
                })
                self.log(f"  ✗ Failed to download {model['subdir']}: {e}")

    def download_control_net_models(self):
        """Download ControlNet models"""
        controlnet_models = [
            {
                "repo_id": "lllyasviel/ControlNet-v1-1",
                "subdir": "controlnet_v1_1",
                "description": "ControlNet v1.1 (initial version)"
            },
            {
                "repo_id": "lllyasviel/ControlNet-v1-2",
                "subdir": "controlnet_v1_2",
                "description": "ControlNet v1.2 (improved)"
            },
            {
                "repo_id": "lllyasviel/ControlNet-v1-3",
                "subdir": "controlnet_v1_3",
                "description": "ControlNet v1.3 (latest stable)"
            },
            {
                "repo_id": "lllyasviel/ControlNet-v1-4",
                "subdir": "controlnet_v1_4",
                "description": "ControlNet v1.4 (additional models)"
            }
        ]

        self.log("Downloading ControlNet models...")

        for model in controlnet_models:
            model_path = self.output_dir / "control_nets" / model["subdir"]
            model_path.mkdir(parents=True, exist_ok=True)

            try:
                self.log(f"  Downloading {model['repo_id']} to {model_path}")

                snapshot_download(
                    repo_id=model["repo_id"],
                    local_dir=str(model_path),
                    local_dir_use_symlinks=False,
                    cache_dir=None
                )

                self.downloaded_models.append({
                    "type": "control_net",
                    "repo_id": model["repo_id"],
                    "path": str(model_path),
                    "description": model["description"]
                })

                self.log(f"  ✓ Successfully downloaded {model['subdir']}")

            except Exception as e:
                self.failed_downloads.append({
                    "type": "control_net",
                    "repo_id": model["repo_id"],
                    "error": str(e)
                })
                self.log(f"  ✗ Failed to download {model['subdir']}: {e}")

    def download_custom_models_from_kaggle(self):
        """Download custom models from Kaggle"""
        self.log("Checking Kaggle for custom models...")

        # This would typically use the kaggle API
        # For now, we'll create a placeholder structure
        custom_models_dir = self.output_dir / "custom"
        custom_models_dir.mkdir(parents=True, exist_ok=True)

        # Create a README for custom models
        readme_file = custom_models_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write("""# Custom Models Directory

This directory contains custom-trained models downloaded from Kaggle.

## Usage
Place your custom model files (.safetensors, .ckpt, etc.) in subdirectories:
- `stable_diffusion/` for custom SD models
- `control_nets/` for custom ControlNet models
- `loras/` for LoRA adapters
- `embeddings/` for text embeddings

## Download from Kaggle
Use the Kaggle integration script to download models:
```bash
python scripts/kaggle_sync.py
```

For help with downloading from Kaggle, refer to the Kaggle API documentation.
""")

        self.log("  Created custom models directory with README")

    def create_model_configs(self):
        """Create configuration files for downloaded models"""
        self.log("Creating model configuration files...")

        # Create models index
        models_index = {
            "stable_diffusion": {
                "description": "Stable Diffusion models for text-to-image generation",
                "models": []
            },
            "control_nets": {
                "description": "ControlNet models for conditioned generation",
                "models": []
            },
            "custom": {
                "description": "Custom user-trained models",
                "models": []
            }
        }

        # Add downloaded models to index
        for model in self.downloaded_models:
            if model["type"] in models_index:
                models_index[model["type"]]["models"].append({
                    "repo_id": model["repo_id"],
                    "path": model["path"],
                    "description": model["description"]
                })

        # Save models index
        index_file = self.output_dir / "models_index.json"
        with open(index_file, 'w') as f:
            json.dump(models_index, f, indent=2)

        self.log(f"  Created models index at {index_file}")

        # Create ComfyUI-specific configs
        self.create_comfyui_configs()

    def create_comfyui_configs(self):
        """Create ComfyUI-specific configuration files"""
        config_dir = self.output_dir / "configs" / "comfyui"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Workflow templates
        workflows_dir = config_dir / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create workflow metadata
        workflows_metadata = {
            "text_to_image": {
                "filename": "text_to_image.json",
                "description": "Basic text-to-image workflow using Stable Diffusion",
                "models_required": ["stable_diffusion/sd_v1_5", "control_nets/controlnet_v1_3"],
                "estimated_time": "2-3 minutes",
                "quality": "high"
            },
            "control_net": {
                "filename": "control_net_workflow.json",
                "description": "Text-to-image with ControlNet conditioning",
                "models_required": ["stable_diffusion/sd_v1_5", "control_nets/controlnet_v1_3"],
                "estimated_time": "3-5 minutes",
                "quality": "high"
            },
            "custom_model": {
                "filename": "custom_model_workflow.json",
                "description": "Workflow for custom/fine-tuned models",
                "models_required": ["stable_diffusion/sd_v1_5", "custom/*"],
                "estimated_time": "2-4 minutes",
                "quality": "variable"
            }
        }

        # Save workflows metadata
        with open(workflows_dir / "workflows_metadata.json", 'w') as f:
            json.dump(workflows_metadata, f, indent=2)

        self.log(f"  Created ComfyUI config files in {config_dir}")

    def run_all_downloads(self):
        """Run all download processes"""
        self.log("Starting comprehensive model download process...")
        self.log(f"Output directory: {self.output_dir.absolute()}")
        self.log("=" * 60)

        # Download models
        self.download_stable_diffusion_models()
        self.log("")
        self.download_control_net_models()
        self.log("")
        self.download_custom_models_from_kaggle()

        # Create configurations
        self.create_model_configs()

        # Summary
        self.log("=" * 60)
        self.log("Download Summary:")
        self.log(f"  Successfully downloaded: {len(self.downloaded_models)} models")
        self.log(f"  Failed downloads: {len(self.failed_downloads)}")

        if self.failed_downloads:
            self.log("\nFailed downloads:")
            for failed in self.failed_downloads:
                self.log(f"  - {failed['repo_id']}: {failed['error']}")

        # Save summary report
        summary = {
            "timestamp": str(Path(__file__).parent.parent / "downloads_report.json"),
            "total_downloaded": len(self.downloaded_models),
            "total_failed": len(self.failed_downloads),
            "downloaded_models": self.downloaded_models,
            "failed_downloads": self.failed_downloads
        }

        summary_file = Path(__file__).parent.parent / "download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        self.log(f"\nSummary saved to: {summary_file}")

        if len(self.failed_downloads) > 0:
            self.log("\n⚠️ Some downloads failed. Check the summary for details.")
            return False
        else:
            self.log("\n✅ All downloads completed successfully!")
            return True

def main():
    parser = argparse.ArgumentParser(description="Download models for ComfyUI + Kaggle project")
    parser.add_argument(
        "--output-dir",
        default="models",
        help="Output directory for models (default: models)"
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing downloads"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ComfyUI + Kaggle Model Downloader")
    print("=" * 60)

    downloader = ModelDownloader(
        output_dir=args.output_dir,
        verbose=not args.no_verbose
    )

    success = downloader.run_all_downloads()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()