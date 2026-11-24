#!/usr/bin/env python3
"""
Kaggle integration script for ComfyUI + GPU project.
Handles synchronization of models and datasets between Kaggle and local storage.
"""

import os
import sys
import argparse
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import hashlib

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class KaggleSynchronizer:
    def __init__(self, project_root, verbose=True):
        self.project_root = Path(project_root)
        self.verbose = verbose
        self.log_file = self.project_root / "logs" / "kaggle_sync.log"

        # Create directories
        self.logs_dir = self.project_root / "logs"
        self.kaggle_dir = self.project_root / ".kaggle"
        self.models_dir = self.project_root / "models"
        self.outputs_dir = self.project_root / "outputs"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.kaggle_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"

        if self.verbose:
            print(f"[KaggleSync] {log_entry}")

        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")

    def check_kaggle_credentials(self):
        """Check if Kaggle credentials are properly configured"""
        kaggle_json_path = self.kaggle_dir / "kaggle.json"

        if not kaggle_json_path.exists():
            self.log("Kaggle credentials not found. Please setup kaggle.json", "WARNING")
            self.log(f"Expected location: {kaggle_json_path}", "WARNING")
            self.log("Get credentials from: https://www.kaggle.com/account?tab=apikeys", "WARNING")
            return False

        try:
            with open(kaggle_json_path, 'r') as f:
                creds = json.load(f)

            # Validate credentials structure
            if not all(key in creds for key in ['username', 'key']):
                self.log("Invalid kaggle.json structure. Missing username or key.", "ERROR")
                return False

            self.log("Kaggle credentials validated successfully")
            return True

        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON in kaggle.json: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error reading kaggle.json: {e}", "ERROR")
            return False

    def download_dataset_from_kaggle(self, dataset_id, output_path, filename_only=False):
        """Download a dataset from Kaggle"""
        self.log(f"Downloading dataset: {dataset_id}")

        try:
            # Use kaggle CLI
            output_path.mkdir(parents=True, exist_ok=True)

            cmd = [
                'kaggle', 'datasets', 'download', '-d', dataset_id,
                '-p', str(output_path),
                '--unzip'
            ]

            if filename_only:
                # Just list available files
                cmd = ['kaggle', 'datasets', 'files', '-d', dataset_id]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode != 0:
                self.log(f"Failed to download dataset {dataset_id}: {result.stderr}", "ERROR")
                return False

            self.log(f"Successfully downloaded dataset: {dataset_id}")
            return True

        except FileNotFoundError:
            self.log("Kaggle command not found. Please install Kaggle CLI.", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error downloading dataset {dataset_id}: {e}", "ERROR")
            return False

    def upload_dataset_to_kaggle(self, local_path, dataset_id, dataset_slug=None):
        """Upload a dataset to Kaggle"""
        self.log(f"Uploading dataset to Kaggle: {dataset_id}")

        try:
            # Create a .gitignore file for temporary files
            gitignore = local_path / ".gitignore"
            with open(gitignore, 'w') as f:
                f.write("*.tmp\n*.temp\n__pycache__/\n*.log\n")

            cmd = [
                'kaggle', 'datasets', 'create', '-d', dataset_id,
                '-p', str(local_path),
                '--force'
            ]

            if dataset_slug:
                cmd.extend(['--slug', dataset_slug])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode != 0:
                self.log(f"Failed to upload dataset to Kaggle: {result.stderr}", "ERROR")
                return False

            self.log(f"Successfully uploaded dataset to Kaggle: {dataset_id}")
            return True

        except Exception as e:
            self.log(f"Error uploading dataset to Kaggle: {e}", "ERROR")
            return False

    def sync_custom_models(self):
        """Sync custom models from Kaggle to local storage"""
        self.log("Syncing custom models from Kaggle...")

        # Define custom models to sync
        custom_models = [
            {
                "dataset_id": "username/custom-sd-models",
                "local_subdir": "stable_diffusion",
                "description": "Custom Stable Diffusion models"
            },
            {
                "dataset_id": "username/custom-controlnets",
                "local_subdir": "control_nets",
                "description": "Custom ControlNet models"
            },
            {
                "dataset_id": "username/custom-loras",
                "local_subdir": "loras",
                "description": "LoRA adapters for fine-tuning"
            },
            {
                "dataset_id": "username/custom-embeddings",
                "local_subdir": "embeddings",
                "description": "Text embeddings and prompts"
            }
        ]

        synced_count = 0

        for model in custom_models:
            self.log(f"\nSyncing: {model['description']}")
            self.log(f"  Dataset: {model['dataset_id']}")

            local_dir = self.models_dir / model['local_subdir']
            local_dir.mkdir(parents=True, exist_ok=True)

            # Check if already synced (using file hashes if available)
            if self.check_directory_hash(local_dir, f"hash_{model['local_subdir']}.txt"):
                self.log(f"  Already synced, skipping...")
                continue

            # Download from Kaggle
            success = self.download_dataset_from_kaggle(
                model['dataset_id'], local_dir
            )

            if success:
                # Save hash for future comparison
                self.save_directory_hash(local_dir, f"hash_{model['local_subdir']}.txt")
                synced_count += 1
                self.log(f"  ✓ Successfully synced {model['local_subdir']}")
            else:
                self.log(f"  ✗ Failed to sync {model['local_subdir']}")

        self.log(f"\nCustom models sync complete: {synced_count}/{len(custom_models)} synced")
        return synced_count

    def sync_outputs_to_kaggle(self):
        """Sync generated outputs to Kaggle"""
        self.log("Syncing generated outputs to Kaggle...")

        # Define output datasets to sync
        output_datasets = [
            {
                "dataset_id": "username/comfyui-generated-images",
                "local_path": "outputs/generated",
                "description": "Generated images from ComfyUI"
            },
            {
                "dataset_id": "username/comfyui-workflows",
                "local_path": "ComfyUI/user/default/workflows",
                "description": "ComfyUI workflow files"
            },
            {
                "dataset_id": "username/comfyui-logs",
                "local_path": "logs",
                "description": "Processing logs and reports"
            }
        ]

        synced_count = 0

        for dataset in output_datasets:
            self.log(f"\nSyncing: {dataset['description']}")
            self.log(f"  Dataset: {dataset['dataset_id']}")

            local_path = Path(dataset['local_path'])

            if not local_path.exists() or not any(local_path.iterdir()):
                self.log(f"  No data to sync in {local_path}", "WARNING")
                continue

            # Create archive directory
            archive_dir = self.project_root / "archives" / dataset['dataset_id'].replace('/', '_')
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Copy data to archive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = archive_dir / f"archive_{timestamp}"
            final_path.mkdir(parents=True, exist_ok=True)

            # Copy files (this is a simplified version)
            for item in local_path.iterdir():
                if item.is_file():
                    dest = final_path / item.name
                    self._safe_copy(item, dest)
                elif item.is_dir():
                    dest = final_path / item.name
                    self._safe_copy(item, dest)

            # Upload to Kaggle
            success = self.upload_dataset_to_kaggle(
                final_path, dataset['dataset_id']
            )

            if success:
                synced_count += 1
                self.log(f"  ✓ Successfully synced {dataset['dataset_id']}")
            else:
                self.log(f"  ✗ Failed to sync {dataset['dataset_id']}")

        self.log(f"\nOutput sync complete: {synced_count}/{len(output_datasets)} synced")
        return synced_count

    def sync_models_to_kaggle(self):
        """Sync local models to Kaggle (for sharing)"""
        self.log("Syncing local models to Kaggle...")

        # Define models to sync
        models_to_sync = [
            {
                "source_path": "models/stable_diffusion",
                "dataset_id": "username/shared-sd-models",
                "description": "Shared Stable Diffusion models"
            },
            {
                "source_path": "models/control_nets",
                "dataset_id": "username/shared-controlnets",
                "description": "Shared ControlNet models"
            }
        ]

        synced_count = 0

        for model in models_to_sync:
            self.log(f"\nSyncing: {model['description']}")
            self.log(f"  Source: {model['source_path']}")
            self.log(f"  Dataset: {model['dataset_id']}")

            source_path = Path(model['source_path'])

            if not source_path.exists() or not any(source_path.iterdir()):
                self.log(f"  No models to sync in {source_path}", "WARNING")
                continue

            # Create temporary archive
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"models_{timestamp}"
            temp_archive = self.project_root / "temp" / archive_name
            temp_archive.mkdir(parents=True, exist_ok=True)

            # Copy models to archive
            for item in source_path.iterdir():
                self._safe_copy(item, temp_archive / item.name)

            # Upload to Kaggle
            success = self.upload_dataset_to_kaggle(
                temp_archive, model['dataset_id']
            )

            if success:
                synced_count += 1
                self.log(f"  ✓ Successfully synced {model['dataset_id']}")
            else:
                self.log(f"  ✗ Failed to sync {model['dataset_id']}")

        self.log(f"\nModel sync complete: {synced_count}/{len(models_to_sync)} synced")
        return synced_count

    def check_directory_hash(self, directory, hash_file_name):
        """Check if directory content matches stored hash"""
        hash_file = directory.parent / hash_file_name

        if not hash_file.exists():
            return False

        try:
            # Calculate current directory hash
            current_hash = self._calculate_directory_hash(directory)

            # Read stored hash
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()

            return current_hash == stored_hash

        except Exception as e:
            self.log(f"Error checking directory hash: {e}", "WARNING")
            return False

    def save_directory_hash(self, directory, hash_file_name):
        """Save directory content hash for future comparison"""
        hash_file = directory.parent / hash_file_name

        try:
            current_hash = self._calculate_directory_hash(directory)

            with open(hash_file, 'w') as f:
                f.write(current_hash)

            self.log(f"  Directory hash saved to {hash_file}")

        except Exception as e:
            self.log(f"Error saving directory hash: {e}", "WARNING")

    def _calculate_directory_hash(self, directory):
        """Calculate hash of directory contents"""
        hasher = hashlib.md5()

        for item in sorted(directory.iterdir()):
            if item.is_file():
                with open(item, 'rb') as f:
                    hasher.update(f.read())
            elif item.is_dir():
                hasher.update(self._calculate_directory_hash(item).encode())

        return hasher.hexdigest()

    def _safe_copy(self, src, dst):
        """Safely copy a file or directory"""
        try:
            if src.is_file():
                import shutil
                shutil.copy2(src, dst)
            elif src.is_dir():
                import shutil
                shutil.copytree(src, dst, dirs_exist_ok=True)
        except Exception as e:
            self.log(f"Error copying {src} to {dst}: {e}", "ERROR")

    def create_sync_report(self, sync_results):
        """Create a summary report of sync operations"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "sync_results": sync_results,
            "status": "completed"
        }

        report_file = self.project_root / "kaggle_sync_report.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"\nSync report saved to: {report_file}")

    def run_full_sync(self, mode="all"):
        """Run full synchronization process"""
        self.log("=" * 60)
        self.log("Starting Kaggle synchronization process")
        self.log(f"Mode: {mode}")
        self.log("Project root: {self.project_root}")
        self.log("=" * 60)

        # Check Kaggle credentials
        if not self.check_kaggle_credentials():
            self.log("Please setup Kaggle credentials first", "ERROR")
            return False

        sync_results = {}
        success = True

        try:
            if mode in ["all", "custom"]:
                custom_synced = self.sync_custom_models()
                sync_results["custom_models"] = {
                    "status": "completed",
                    "synced_count": custom_synced
                }

            if mode in ["all", "outputs"]:
                outputs_synced = self.sync_outputs_to_kaggle()
                sync_results["outputs"] = {
                    "status": "completed",
                    "synced_count": outputs_synced
                }

            if mode in ["all", "models"]:
                models_synced = self.sync_models_to_kaggle()
                sync_results["models"] = {
                    "status": "completed",
                    "synced_count": models_synced
                }

            # Create sync report
            self.create_sync_report(sync_results)

            # Summary
            self.log("\n" + "=" * 60)
            self.log("Synchronization Summary:")
            for operation, result in sync_results.items():
                self.log(f"  {operation}: {result['synced_count']} items synced")

            self.log("\n✅ All synchronization tasks completed successfully!")
            return True

        except Exception as e:
            self.log(f"Error during synchronization: {e}", "ERROR")
            success = False

        # Save error report
        if not success:
            error_report = {
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            }

            error_file = self.project_root / "kaggle_sync_error_report.json"
            with open(error_file, 'w') as f:
                json.dump(error_report, f, indent=2)

            self.log(f"\nError report saved to: {error_file}")

        return success

def main():
    parser = argparse.ArgumentParser(
        description="Kaggle integration script for ComfyUI + GPU project"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "custom", "outputs", "models"],
        default="all",
        help="Synchronization mode (default: all)"
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--test-credentials",
        action="store_true",
        help="Test Kaggle credentials only"
    )

    args = parser.parse_args()

    synchronizer = KaggleSynchronizer(
        project_root=args.project_root,
        verbose=not args.no_verbose
    )

    if args.test_credentials:
        print("Testing Kaggle credentials...")
        success = synchronizer.check_kaggle_credentials()
        sys.exit(0 if success else 1)

    success = synchronizer.run_full_sync(mode=args.mode)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()