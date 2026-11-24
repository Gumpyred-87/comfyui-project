#!/usr/bin/env python3
"""
ComfyUI launcher script for ComfyUI + Kaggle project.
Launches ComfyUI with proper environment configuration.
"""

import os
import sys
import subprocess
import time
import argparse
import signal
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class ComfyUILauncher:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.comfyui_dir = self.project_root / "ComfyUI"
        self.verbose = True

        # Setup environment variables
        self.setup_environment()

    def setup_environment(self):
        """Setup environment variables for ComfyUI"""
        # ComfyUI paths
        os.environ['COMFYUI_ROOT'] = str(self.comfyui_dir)

        # Model directories
        self.models_dir = self.project_root / "models"
        os.environ['MODEL_DIR'] = str(self.models_dir / "stable_diffusion")
        os.environ['CONTROLNET_DIR'] = str(self.models_dir / "control_nets")
        os.environ['CUSTOM_DIR'] = str(self.models_dir / "custom")

        # Output directories
        self.outputs_dir = self.project_root / "outputs"
        os.environ['OUTPUT_DIR'] = str(self.outputs_dir / "generated")
        os.environ['TEMP_DIR'] = str(self.outputs_dir / "temporary")

        # Create directories
        for dir_path in [
            self.models_dir / "stable_diffusion",
            self.models_dir / "control_nets",
            self.models_dir / "custom",
            self.outputs_dir / "generated",
            self.outputs_dir / "temporary",
            self.project_root / "logs"
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create ComfyUI user directories
        comfyui_user_dir = self.comfyui_dir / "user" / "default"
        comfyui_user_dir.mkdir(parents=True, exist_ok=True)

        # Create workflows directory
        workflows_dir = comfyui_user_dir / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create history directory
        history_dir = comfyui_user_dir / "history"
        history_dir.mkdir(parents=True, exist_ok=True)

        # Create input directory
        input_dir = comfyui_user_dir / "input"
        input_dir.mkdir(parents=True, exist_ok=True)

        self.log(f"Environment setup complete")
        self.log(f"ComfyUI root: {self.comfyui_dir}")
        self.log(f"Models dir: {self.models_dir}")
        self.log(f"Outputs dir: {self.outputs_dir}")

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        if self.verbose:
            print(f"[ComfyUILauncher] {log_entry}")

    def check_comfyui_installation(self):
        """Check if ComfyUI is properly installed"""
        self.log("Checking ComfyUI installation...")

        # Check if ComfyUI directory exists
        if not self.comfyui_dir.exists():
            self.log("ERROR: ComfyUI directory not found")
            self.log(f"Expected location: {self.comfyui_dir}")
            self.log("Please ensure ComfyUI is properly installed")
            return False

        # Check for key ComfyUI files
        key_files = [
            self.comfyui_dir / "main.py",
            self.comfyui_dir / "__init__.py",
            self.comfyui_dir / "requirements.txt"
        ]

        missing_files = []
        for file_path in key_files:
            if not file_path.exists():
                missing_files.append(file_path.name)

        if missing_files:
            self.log(f"WARNING: Missing key files: {missing_files}")
            self.log("ComfyUI installation may be incomplete")
        else:
            self.log("✅ ComfyUI installation appears complete")

        return True

    def check_models_available(self):
        """Check if required models are available"""
        self.log("Checking model availability...")

        # Required model directories
        required_dirs = [
            ("stable_diffusion", "Stable Diffusion models"),
            ("control_nets", "ControlNet models"),
            ("custom", "Custom models")
        ]

        missing_dirs = []
        available_dirs = []

        for subdir, description in required_dirs:
            dir_path = self.models_dir / subdir
            if dir_path.exists() and any(dir_path.iterdir()):
                available_dirs.append((subdir, description))
                self.log(f"✅ {description}: Available ({subdir}/)")
            else:
                missing_dirs.append((subdir, description))
                self.log(f"⚠️  {description}: Not available ({subdir}/)")

        if missing_dirs:
            self.log(f"\nMissing required model directories: {len(missing_dirs)}")
            for subdir, description in missing_dirs:
                self.log(f"  - {description}: {subdir}/")

        # Check for specific model files
        self.log("\nChecking for key model files...")
        self.check_model_files()

        return len(missing_dirs) == 0

    def check_model_files(self):
        """Check for specific model files that ComfyUI needs"""
        # Look for .safetensors files (preferred format)
        model_extensions = ['.safetensors', '.ckpt', '.pth']
        model_files = []

        for model_dir in self.models_dir.iterdir():
            if model_dir.is_dir():
                for ext in model_extensions:
                    model_files.extend(model_dir.glob(f"*{ext}"))

        if model_files:
            self.log(f"Found {len(model_files)} model files:")
            for model_file in model_files[:10]:  # Show first 10
                size_mb = model_file.stat().st_size / (1024**2)
                self.log(f"  - {model_file.relative_to(self.project_root)} ({size_mb:.1f} MB)")

            if len(model_files) > 10:
                self.log(f"  ... and {len(model_files) - 10} more")

        else:
            self.log("⚠️  No model files found. Models may need to be downloaded.")
            self.log("Run: python scripts/download_models.py")

    def check_port_availability(self, port=8188):
        """Check if port is available"""
        self.log(f"Checking port availability: {port}")

        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('localhost', port))
                s.close()
                self.log(f"✅ Port {port} is available")
                return True
        except OSError as e:
            self.log(f"❌ Port {port} is in use: {e}")
            return False

    def check_system_resources(self):
        """Check system resource availability"""
        self.log("Checking system resources...")

        import psutil

        # CPU information
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=1)
        self.log(f"CPU: {cpu_count} cores, {cpu_percent}% usage")

        # Memory information
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_used_gb = memory.used / (1024**3)
        self.log(f"Memory: {memory_used_gb:.1f} GB / {memory_gb:.1f} GB ({memory.percent}%)")

        # Disk space
        disk_usage = psutil.disk_usage('/')
        disk_gb = disk_usage.total / (1024**3)
        disk_used_gb = disk_usage.used / (1024**3)
        self.log(f"Disk: {disk_used_gb:.1f} GB / {disk_gb:.1f} GB ({disk_usage.percent}%)")

        # Warnings for resource constraints
        warnings = []

        if memory.percent > 90:
            warnings.append("Memory usage is high")

        if disk_usage.percent > 90:
            warnings.append("Disk space is low")

        if cpu_percent > 80:
            warnings.append("CPU usage is high")

        if warnings:
            self.log(f"⚠️  Resource warnings: {', '.join(warnings)}")
        else:
            self.log("✅ System resources are adequate")

    def create_launcher_scripts(self):
        """Create additional launcher scripts"""
        self.log("Creating additional launcher scripts...")

        # Create a simple test script
        test_script = self.project_root / "test_comfyui.py"
        with open(test_script, 'w') as f:
            f.write("""#!/usr/bin/env python3
"""
ComfyUI test script
"""
import subprocess
import time
import requests
import sys
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.launch_comfyui import ComfyUILauncher

def main():
    print("🔍 Testing ComfyUI setup...")

    launcher = ComfyUILauncher(project_root)

    # Check installation
    if not launcher.check_comfyui_installation():
        print("❌ ComfyUI installation check failed")
        sys.exit(1)

    # Check models
    if not launcher.check_models_available():
        print("⚠️  Model check failed but continuing...")

    # Check system resources
    launcher.check_system_resources()

    print("\n✅ ComfyUI setup check complete")
    print("You can now launch ComfyUI with: python -m comfyui")
    print("Or use the launcher script: python scripts/launch_comfyui.py --start")

if __name__ == "__main__":
    main()
""")

        test_script.chmod(0o755)

        # Create workflow templates
        workflows_dir = self.project_root / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple workflow template
        workflow_template = workflows_dir / "template_workflow.json"
        with open(workflow_template, 'w') as f:
            json.dump({
                "name": "Template Workflow",
                "version": "1.0",
                "author": "ComfyUI Project",
                "date_created": datetime.now().isoformat(),
                "description": "Template workflow for ComfyUI",
                "nodes": [],
                "parameters": {}
            }, f, indent=2)

        self.log(f"Created test script at {test_script}")
        self.log(f"Created workflow template at {workflow_template}")

    def launch_comfyui(self, port=8188):
        """Launch ComfyUI server"""
        self.log(f"Launching ComfyUI on port {port}...")

        # Check if ComfyUI is already running
        if not self.check_port_availability(port):
            self.log(f"Port {port} is not available. Trying alternative ports...")
            ports_to_try = [8188, 8189, 8190, 8191, 8192]
            for alt_port in ports_to_try[1:]:
                if self.check_port_availability(alt_port):
                    port = alt_port
                    break
            else:
                self.log("ERROR: No available ports found")
                return False

        # Prepare launch command
        cmd = [
            sys.executable, '-m', 'comfyui',
            '--port', str(port)
        ]

        # Add additional arguments if available
        if self.comfyui_dir.exists():
            cmd.extend(['--root', str(self.comfyui_dir)])

        self.log(f"Command: {' '.join(cmd)}")

        try:
            # Start ComfyUI process
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=os.environ
            )

            # Store process for later management
            self.comfyui_process = process

            # Wait a moment to see if process starts successfully
            time.sleep(3)

            # Check if process is still running
            if process.poll() is not None:
                # Process terminated, check output
                stdout, stderr = process.communicate()
                self.log(f"ComfyUI process terminated early")
                self.log(f"STDOUT: {stdout}")
                self.log(f"STDERR: {stderr}")
                return False

            self.log(f"✅ ComfyUI launched successfully on port {port}")
            self.log(f"Open browser to: http://localhost:{port}")
            return True

        except Exception as e:
            self.log(f"ERROR: Failed to launch ComfyUI: {e}")
            return False

    def stop_comfyui(self):
        """Stop ComfyUI if running"""
        if hasattr(self, 'comfyui_process') and self.comfyui_process:
            self.log("Stopping ComfyUI...")
            try:
                self.comfyui_process.terminate()
                self.comfyui_process.wait(timeout=10)
                self.log("✅ ComfyUI stopped successfully")
            except subprocess.TimeoutExpired:
                self.log("⚠️  Force stopping ComfyUI...")
                self.comfyui_process.kill()
                self.comfyui_process.wait()
                self.log("✅ ComfyUI force stopped")
            except Exception as e:
                self.log(f"Error stopping ComfyUI: {e}")
            finally:
                self.comfyui_process = None

    def run_comprehensive_check(self):
        """Run comprehensive system check"""
        self.log("Running comprehensive ComfyUI system check...")
        self.log("=" * 60)

        checks = [
            ("ComfyUI Installation", self.check_comfyui_installation),
            ("Model Availability", self.check_models_available),
            ("Port Availability", lambda: self.check_port_availability()),
            ("System Resources", self.check_system_resources),
            ("Environment Setup", lambda: True)  # Already done in __init__
        ]

        results = {}
        all_passed = True

        for check_name, check_func in checks:
            self.log(f"\n📋 Running check: {check_name}")
            try:
                passed = check_func()
                results[check_name] = passed
                status = "✅ PASSED" if passed else "❌ FAILED"
                self.log(f"  Result: {status}")
                if not passed:
                    all_passed = False
            except Exception as e:
                self.log(f"  Result: ❌ ERROR - {e}")
                results[check_name] = False
                all_passed = False

        self.log("\n" + "=" * 60)
        self.log("SYSTEM CHECK SUMMARY:")
        for check_name, passed in results.items():
            status = "✅" if passed else "❌"
            self.log(f"  {status} {check_name}")

        if all_passed:
            self.log("\n🎉 All checks passed! Ready to launch ComfyUI.")
        else:
            self.log("\n⚠️  Some checks failed. Please review the issues above.")

        return all_passed

    def create_launch_summary(self, port, success):
        """Create launch summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "port": port,
            "success": success,
            "project_root": str(self.project_root),
            "comfyui_dir": str(self.comfyui_dir),
            "environment_variables": {
                key: value for key, value in os.environ.items()
                if key.startswith(('COMFYUI', 'MODEL', 'OUTPUT', 'TEMP'))
            },
            "model_directories": {
                "stable_diffusion": str(self.models_dir / "stable_diffusion"),
                "control_nets": str(self.models_dir / "control_nets"),
                "custom": str(self.models_dir / "custom")
            },
            "output_directories": {
                "generated": str(self.outputs_dir / "generated"),
                "temporary": str(self.outputs_dir / "temporary")
            }
        }

        summary_file = self.project_root / "comfyui_launch_summary.json"

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        self.log(f"Launch summary saved to: {summary_file}")
        return summary_file

def main():
    parser = argparse.ArgumentParser(description="ComfyUI launcher script for ComfyUI + Kaggle project")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8188,
        help="Port to use for ComfyUI (default: 8188)"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Run system check only, don't launch"
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start ComfyUI after check"
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop ComfyUI if running"
    )
    parser.add_argument(
        "--create-scripts",
        action="store_true",
        help="Create additional launcher scripts"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ComfyUI Launcher for ComfyUI + Kaggle Project")
    print("=" * 60)

    launcher = ComfyUILauncher(args.project_root)
    launcher.verbose = not args.no_verbose

    if args.stop:
        launcher.stop_comfyui()
        return 0

    if args.create_scripts:
        launcher.create_launcher_scripts()
        print("\n✅ Additional scripts created successfully")
        return 0

    # Run comprehensive check
    if not launcher.run_comprehensive_check():
        print("\n❌ System check failed. Please fix issues before launching.")
        return 1

    if args.check_only:
        print("\n✅ System check complete. Ready to launch.")
        return 0

    # Launch ComfyUI
    print("\n🚀 Launching ComfyUI...")
    success = launcher.launch_comfyui(port=args.port)

    if success:
        print(f"\n🎉 ComfyUI is running on port {args.port}")
        print(f"Open your browser and go to: http://localhost:{args.port}")
        print("Press Ctrl+C to stop ComfyUI")

        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping ComfyUI...")
            launcher.stop_comfyui()
    else:
        print("\n❌ Failed to launch ComfyUI")
        return 1

    return 0

if __name__ == "__main__":
    main()