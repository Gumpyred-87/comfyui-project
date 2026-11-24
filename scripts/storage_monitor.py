#!/usr/bin/env python3
"""
Storage monitoring script for ComfyUI + Kaggle project.
Monitors disk usage, model sizes, and provides cleanup recommendations.
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
import psutil
import humanize

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class StorageMonitor:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.monitoring_report = {
            "timestamp": datetime.now().isoformat(),
            "disk_usage": {},
            "directory_sizes": {},
            "cleanup_recommendations": [],
            "status": "ok"
        }

        # Define monitored directories
        self.monitored_dirs = {
            "models": "Model files (weights, checkpoints)",
            "outputs": "Generated outputs and results",
            "configs": "Configuration files",
            "archives": "Archived data",
            "logs": "Log files",
            "temporary": "Temporary and cache files"
        }

    def get_disk_usage(self, path):
        """Get disk usage statistics for a path"""
        try:
            usage = shutil.disk_usage(path)
            return {
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "usage_percent": (usage.used / usage.total) * 100
            }
        except Exception as e:
            return {"error": str(e)}

    def get_directory_size(self, path, include_hidden=False):
        """Get total size of directory in GB"""
        total_size = 0
        file_count = 0
        dir_count = 0

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                # Filter hidden files/directories if needed
                if not include_hidden:
                    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                    filenames = [f for f in filenames if not f.startswith('.')]

                dir_count += len(dirnames)
                file_count += len(filenames)

                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, IOError):
                        # Skip files that can't be accessed
                        pass

            return {
                "size_gb": total_size / (1024**3),
                "file_count": file_count,
                "dir_count": dir_count,
                "path": str(path)
            }

        except Exception as e:
            return {"error": str(e), "path": str(path)}

    def analyze_large_files(self, path, min_size_mb=100):
        """Find large files in directory"""
        large_files = []

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename

                    try:
                        file_size = filepath.stat().st_size
                        size_mb = file_size / (1024**2)

                        if size_mb >= min_size_mb:
                            large_files.append({
                                "path": str(filepath),
                                "size_mb": size_mb,
                                "size_gb": file_size / (1024**3),
                                "modified": datetime.fromtimestamp(
                                    filepath.stat().st_mtime
                                ).isoformat()
                            })

                    except (OSError, IOError):
                        continue

        except Exception as e:
            return {"error": str(e)}

        return large_files

    def check_duplicate_files(self, path, extensions=None):
        """Check for duplicate files"""
        if extensions is None:
            extensions = ['.json', '.txt', '.py', '.md', '.yaml', '.yml']

        file_hashes = {}
        duplicates = []

        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in extensions):
                        filepath = Path(dirpath) / filename

                        try:
                            file_hash = self._calculate_file_hash(filepath)
                            file_key = (file_hash, filename)

                            if file_key in file_hashes:
                                duplicates.append({
                                    "file1": file_hashes[file_key],
                                    "file2": str(filepath),
                                    "filename": filename,
                                    "hash": file_hash
                                })
                            else:
                                file_hashes[file_key] = str(filepath)

                        except (OSError, IOError):
                            continue

        except Exception as e:
            return {"error": str(e)}

        return duplicates

    def _calculate_file_hash(self, filepath, chunk_size=8192):
        """Calculate MD5 hash of file"""
        hasher = hashlib.md5()

        try:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    hasher.update(data)
            return hasher.hexdigest()
        except (OSError, IOError):
            return None

    def generate_cleanup_recommendations(self):
        """Generate cleanup recommendations based on analysis"""
        recommendations = []

        # Check temporary files
        temp_dir = self.project_root / "outputs" / "temporary"
        if temp_dir.exists():
            temp_size = self.get_directory_size(temp_dir)
            if temp_size.get("size_gb", 0) > 5:  # More than 5GB
                recommendations.append({
                    "type": "cleanup_temporary",
                    "priority": "high",
                    "description": f"Temporary directory ({temp_size.get('size_gb', 0):.2f} GB) is large",
                    "action": "Remove files older than 7 days",
                    "estimated_savings_gb": temp_size.get("size_gb", 0) * 0.3
                })

        # Check for old outputs
        outputs_dir = self.project_root / "outputs" / "generated"
        if outputs_dir.exists():
            old_outputs = self._find_old_files(outputs_dir, days=30)
            if old_outputs:
                recommendations.append({
                    "type": "cleanup_old_outputs",
                    "priority": "medium",
                    "description": f"Found {len(old_outputs)} output files older than 30 days",
                    "action": "Archive or delete old outputs",
                    "estimated_savings_gb": sum(f["size_gb"] for f in old_outputs) * 0.8
                })

        # Check for log files
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            logs_size = self.get_directory_size(logs_dir)
            if logs_size.get("size_gb", 0) > 1:  # More than 1GB
                recommendations.append({
                    "type": "cleanup_logs",
                    "priority": "low",
                    "description": f"Log files ({logs_size.get('size_gb', 0):.2f} GB) accumulated",
                    "action": "Rotate logs, keep recent ones",
                    "estimated_savings_gb": logs_size.get("size_gb", 0) * 0.5
                })

        # Check model cache
        model_cache_dirs = [
            self.project_root / "models" / "stable_diffusion" / "sd_v1_5" / "cache",
            self.project_root / "models" / "control_nets" / "controlnet_v1_3" / "cache",
        ]

        for cache_dir in model_cache_dirs:
            if cache_dir.exists():
                cache_size = self.get_directory_size(cache_dir)
                if cache_size.get("size_gb", 0) > 2:  # More than 2GB
                    recommendations.append({
                        "type": "cleanup_model_cache",
                        "priority": "medium",
                        "description": f"Model cache ({cache_dir.name}) is large ({cache_size.get('size_gb', 0):.2f} GB)",
                        "action": "Clear model cache, download fresh if needed",
                        "estimated_savings_gb": cache_size.get("size_gb", 0)
                    })

        # Check duplicate files
        for dir_name, dir_description in self.monitored_dirs.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                duplicates = self.check_duplicate_files(dir_path)
                if duplicates:
                    total_duplicate_size = sum(
                        min(f.get("size_gb", 0), 0.1) for f in duplicates
                    )
                    recommendations.append({
                        "type": "cleanup_duplicates",
                        "priority": "low",
                        "description": f"Found {len(duplicates)} duplicate {dir_description.lower()}",
                        "action": "Remove duplicate files",
                        "estimated_savings_gb": total_duplicate_size
                    })

        return recommendations

    def _find_old_files(self, directory, days):
        """Find files older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        old_files = []

        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = Path(dirpath) / filename

                    try:
                        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                        if mtime < cutoff_time:
                            file_size = filepath.stat().st_size
                            old_files.append({
                                "path": str(filepath),
                                "size_gb": file_size / (1024**3),
                                "modified": mtime.isoformat()
                            })
                    except (OSError, IOError):
                        continue

        except Exception as e:
            return []

        return old_files

    def generate_comprehensive_report(self):
        """Generate comprehensive storage report"""
        self.log("Generating comprehensive storage report...")

        # Disk usage
        for drive in ['/', 'C:', 'D:']:
            if os.path.exists(drive):
                disk_info = self.get_disk_usage(drive)
                self.monitoring_report["disk_usage"][drive] = disk_info

        # Directory sizes
        for dir_name, description in self.monitored_dirs.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                dir_info = self.get_directory_size(dir_path)
                self.monitoring_report["directory_sizes"][dir_name] = {
                    "description": description,
                    "info": dir_info
                }

        # Large files analysis
        for dir_name in self.monitored_dirs.keys():
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                large_files = self.analyze_large_files(dir_path)
                if large_files:
                    self.monitoring_report["large_files"] = self.monitoring_report.get(
                        "large_files", {}
                    )
                    self.monitoring_report["large_files"][dir_name] = large_files[:10]  # Top 10

        # Generate cleanup recommendations
        self.monitoring_report["cleanup_recommendations"] = self.generate_cleanup_recommendations()

        # Determine overall status
        critical_issues = [
            rec for rec in self.monitoring_report["cleanup_recommendations"]
            if rec["priority"] == "high"
        ]

        if critical_issues:
            self.monitoring_report["status"] = "critical"
        elif any(rec["priority"] == "medium" for rec in self.monitoring_report["cleanup_recommendations"]):
            self.monitoring_report["status"] = "warning"
        else:
            self.monitoring_report["status"] = "ok"

        return self.monitoring_report

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(f"[StorageMonitor] {log_entry}")

    def save_report(self, filename="storage_report.json"):
        """Save monitoring report to file"""
        report_file = self.project_root / filename

        with open(report_file, 'w') as f:
            json.dump(self.monitoring_report, f, indent=2)

        self.log(f"Storage report saved to: {report_file}")
        return report_file

    def print_human_readable_report(self):
        """Print human-readable storage report"""
        print("\n" + "=" * 60)
        print("STORAGE MONITORING REPORT")
        print("=" * 60)

        # Disk usage
        print("\n📊 DISK USAGE:")
        for drive, info in self.monitoring_report["disk_usage"].items():
            if "error" in info:
                print(f"  {drive}: Error - {info['error']}")
            else:
                print(f"  {drive}:")
                print(f"    Total: {info['total_gb']:.2f} GB")
                print(f"    Used:  {info['used_gb']:.2f} GB ({info['usage_percent']:.1f}%)")
                print(f"    Free:  {info['free_gb']:.2f} GB")

        # Directory sizes
        print("\n📁 DIRECTORY SIZES:")
        for dir_name, info in self.monitoring_report["directory_sizes"].items():
            dir_info = info["info"]
            if "error" in dir_info:
                print(f"  {dir_name}: Error - {dir_info['error']}")
            else:
                size_gb = dir_info["size_gb"]
                file_count = dir_info["file_count"]
                print(f"  {dir_name}: {size_gb:.2f} GB ({file_count} files)")

        # Large files
        if "large_files" in self.monitoring_report:
            print("\n⚠️  LARGE FILES (>100MB):")
            for dir_name, files in self.monitoring_report["large_files"].items():
                for file_info in files[:3]:  # Show top 3
                    print(f"  {file_info['path']}: {file_info['size_mb']:.1f} MB")

        # Cleanup recommendations
        recommendations = self.monitoring_report["cleanup_recommendations"]
        if recommendations:
            print("\n🔧 CLEANUP RECOMMENDATIONS:")
            for rec in recommendations:
                priority_emoji = "🔴" if rec["priority"] == "high" else "🟡" if rec["priority"] == "medium" else "🟢"
                print(f"  {priority_emoji} {rec['description']}")
                print(f"     Action: {rec['action']}")
                print(f"     Estimated savings: {rec['estimated_savings_gb']:.2f} GB")
        else:
            print("\n✅ No cleanup recommendations needed")

        # Status
        status_emoji = "🔴" if self.monitoring_report["status"] == "critical" else "🟡" if self.monitoring_report["status"] == "warning" else "🟢"
        print(f"\n📈 STATUS: {status_emoji} {self.monitoring_report['status'].upper()}")

        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(description="Storage monitoring script for ComfyUI + Kaggle project")
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
        "--report-only",
        action="store_true",
        help="Generate report only, no cleanup actions"
    )
    parser.add_argument(
        "--output-file",
        default="storage_report.json",
        help="Output filename for JSON report (default: storage_report.json)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("ComfyUI + Kaggle Storage Monitor")
    print("=" * 60)

    monitor = StorageMonitor(args.project_root)

    # Generate report
    monitor.generate_comprehensive_report()

    # Print human-readable report
    monitor.print_human_readable_report()

    # Save JSON report
    report_file = monitor.save_report(args.output_file)

    # If not report-only, perform cleanup actions
    if not args.report_only:
        print("\n🔄 Performing cleanup actions...")
        monitor.perform_cleanup_actions()

    return 0

if __name__ == "__main__":
    sys.exit(main())