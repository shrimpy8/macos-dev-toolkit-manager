#!/usr/bin/env python3
"""
macOS Dev Toolkit Manager (safe_update.py)
==========================================

A safe, interactive tool for upgrading macOS development tools:
- Homebrew packages
- Conda package manager
- Python (via Conda or Homebrew)
- npm and global npm packages

DISCLAIMER:
-----------
⚠️  USE AT YOUR OWN RISK ⚠️

This script modifies your system's package managers and installed software.
While designed with safety features, there are inherent risks:

1. BACKUP YOUR WORK: Always commit/push code before running upgrades
2. COMPATIBILITY: Upgrades may break existing projects or dependencies
3. ROLLBACK: While snapshots are saved, manual rollback may be required
4. TESTING: Always test your development environment after major upgrades
5. CONDA ENVIRONMENTS: This only upgrades base conda, not other environments
6. NO WARRANTY: This software is provided "as-is" without any warranties

SAFETY FEATURES:
----------------
✅ Patch updates (x.x.Z): Auto-approved (e.g., 3.12.11 → 3.12.12)
⚠️  Minor updates (x.Y.x): Requires confirmation (e.g., npm 10.x → 11.x)
🛑 Major updates (X.x.x): Requires manual review (e.g., Python 3.12 → 3.13)
📸 Pre-upgrade snapshots saved to ~/upgrade-logs/
📝 All commands logged with timestamps

Author: Generated via Warp AI
License: MIT (Free to use and modify)
Version: 1.2.0
Script: safe_update.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Try to import rich library for better UI experience
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Confirm, Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Using plain output.")
    print("Install with: pip install rich")


class SystemUpgradeManager:
    """
    Main class for managing system package upgrades.
    
    This class provides methods to check for updates and safely upgrade:
    - Homebrew (macOS package manager)
    - Conda (Python package/environment manager)
    - Python (via Conda)
    - npm (Node.js package manager)
    
    All operations are logged and pre-upgrade snapshots are saved for rollback.
    """
    
    def __init__(self):
        """
        Initialize the upgrade manager.
        
        Creates:
        - ~/upgrade-logs/ directory for logs and snapshots
        - Timestamp for this session
        - Log file and snapshot file paths
        - Rich console if available
        """
        self.log_dir = Path.home() / "upgrade-logs"
        self.log_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"upgrade_{self.timestamp}.log"
        self.snapshot_file = self.log_dir / f"snapshot_{self.timestamp}.json"
        
        # Initialize rich console if available for better UI
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        
        # Dictionary to store current system state
        self.snapshot = {}
    
    def print(self, text: str, style: str = ""):
        """
        Print text with optional rich formatting.
        
        Args:
            text: Text to print
            style: Rich style string (e.g., "bold red", "green")
        """
        if self.console:
            self.console.print(text, style=style)
        else:
            print(text)
    
    def print_panel(self, text: str, title: str = ""):
        """
        Print a bordered panel with title.
        
        Args:
            text: Panel content
            title: Optional panel title
        """
        if self.console:
            self.console.print(Panel(text, title=title))
        else:
            print(f"\n{'='*60}")
            if title:
                print(f"{title}")
                print(f"{'='*60}")
            print(text)
            print(f"{'='*60}\n")
    
    def confirm(self, message: str) -> bool:
        """
        Ask user for yes/no confirmation.
        
        Args:
            message: Question to ask user
            
        Returns:
            True if user confirms, False otherwise
        """
        if self.console:
            return Confirm.ask(message)
        else:
            response = input(f"{message} [y/n]: ").strip().lower()
            return response in ['y', 'yes']
    
    def log(self, message: str):
        """
        Log message to file and display on console.
        
        All log entries are timestamped and saved to the log file
        in ~/upgrade-logs/ for debugging and audit purposes.
        
        Args:
            message: Message to log
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")
        
        self.print(f"[dim]{message}[/dim]")
    
    def run_command(self, cmd: str, capture: bool = True) -> Tuple[int, str, str]:
        """
        Execute a shell command and return the results.
        
        Args:
            cmd: Shell command to execute
            capture: Whether to capture output (default: True)
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
            
        Note:
            All commands are logged before execution.
            Commands are executed using /bin/zsh shell.
        """
        self.log(f"Running: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=capture,
                text=True,
                executable="/bin/zsh"
            )
            
            if capture:
                return result.returncode, result.stdout.strip(), result.stderr.strip()
            else:
                return result.returncode, "", ""
        except Exception as e:
            self.log(f"Error running command: {e}")
            return 1, "", str(e)
    
    def parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """
        Parse semantic version string into tuple.
        
        Args:
            version_str: Version string (e.g., "3.12.5", "v10.2.1", "conda 25.9.1")
            
        Returns:
            Tuple of (major, minor, patch) as integers
            Returns (0, 0, 0) if parsing fails
            
        Examples:
            "3.12.5" → (3, 12, 5)
            "v10.2.1" → (10, 2, 1)
            "conda 25.9.1" → (25, 9, 1)
        """
        try:
            # Remove common prefixes (v, conda, etc.)
            version_str = version_str.replace('v', '').replace('conda', '').strip()
            parts = version_str.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except:
            return (0, 0, 0)
    
    def is_safe_upgrade(self, current: str, latest: str) -> Tuple[bool, str]:
        """
        Determine if an upgrade is safe based on semantic versioning.
        
        Safety Rules:
        - Patch updates (x.x.Z): SAFE - Auto-approved
        - Minor updates (x.Y.x): CAUTION - Requires confirmation
        - Major updates (X.x.x): RISKY - Requires manual review
        
        Args:
            current: Current version string
            latest: Latest available version string
            
        Returns:
            Tuple of (is_safe: bool, reason: str)
            
        Examples:
            ("3.12.11", "3.12.12") → (True, "Patch update (safe)")
            ("10.5.0", "11.0.0") → (False, "Major version upgrade (requires manual review)")
        """
        curr_v = self.parse_version(current)
        latest_v = self.parse_version(latest)
        
        if curr_v == latest_v:
            return False, "Already up to date"
        
        if latest_v[0] > curr_v[0]:
            return False, "Major version upgrade (requires manual review)"
        
        if latest_v[1] > curr_v[1]:
            return False, "Minor version upgrade (requires confirmation)"
        
        if latest_v[2] > curr_v[2]:
            return True, "Patch update (safe)"
        
        return False, "Downgrade not recommended"
    
    def save_snapshot(self):
        """
        Save current system state to JSON file.
        
        Snapshots include:
        - Current versions of all package managers
        - List of outdated packages
        - Timestamp of capture
        
        Snapshots are saved to ~/upgrade-logs/snapshot_<timestamp>.json
        and can be used to manually rollback changes if needed.
        """
        self.log("Creating system snapshot...")
        
        with open(self.snapshot_file, "w") as f:
            json.dump(self.snapshot, f, indent=2)
        
        self.print(f"[green]✓[/green] Snapshot saved to: {self.snapshot_file}")
    
    # ==================== HOMEBREW ====================
    
    def check_homebrew(self) -> Dict:
        """
        Check Homebrew version and list outdated packages.
        
        Process:
        1. Get current Homebrew version
        2. Update Homebrew package index (brew update)
        3. Check for outdated formulae and casks
        4. Save results to snapshot
        
        Returns:
            Dictionary containing:
            - version: Current Homebrew version
            - outdated_count: Number of outdated packages
            - outdated_packages: List of package details
        """
        self.print("\n[bold cyan]Checking Homebrew...[/bold cyan]")
        
        # Get current Homebrew version
        code, version, _ = self.run_command("brew --version | head -1")
        current_version = version.split()[1] if code == 0 else "unknown"
        
        # Update Homebrew package index
        self.log("Updating Homebrew...")
        self.run_command("brew update > /dev/null 2>&1")
        
        # Get list of outdated packages
        code, outdated, _ = self.run_command("brew outdated --json")
        outdated_packages = []
        
        if code == 0 and outdated:
            try:
                data = json.loads(outdated)
                # Parse both formulae (CLI tools) and casks (GUI apps)
                for item in data.get('formulae', []) + data.get('casks', []):
                    outdated_packages.append({
                        'name': item['name'],
                        'current': item['installed_versions'][0] if item.get('installed_versions') else 'unknown',
                        'latest': item['current_version']
                    })
            except:
                pass
        
        # Store results in snapshot
        info = {
            'version': current_version,
            'outdated_count': len(outdated_packages),
            'outdated_packages': outdated_packages
        }
        
        self.snapshot['homebrew'] = info
        
        # Display summary
        if outdated_packages:
            self.print(f"Found {len(outdated_packages)} outdated package(s)")
        else:
            self.print("[green]✓ All Homebrew packages up to date[/green]")
        
        return info
    
    def upgrade_homebrew(self):
        """
        Upgrade Homebrew packages with safety checks.
        
        Process:
        1. Check for outdated packages
        2. Display table of available upgrades with safety ratings
        3. Auto-upgrade safe (patch) packages
        4. Prompt user for unsafe (minor/major) packages
        5. Run brew cleanup if user confirms
        
        Safety:
        - Patch updates: Upgraded automatically
        - Minor/major updates: Require user confirmation
        """
        info = self.check_homebrew()
        
        if info['outdated_count'] == 0:
            return
        
        # Display table of outdated packages with safety ratings
        if self.console:
            table = Table(title="Outdated Homebrew Packages")
            table.add_column("Package", style="cyan")
            table.add_column("Current", style="yellow")
            table.add_column("Latest", style="green")
            table.add_column("Safety", style="magenta")
            
            for pkg in info['outdated_packages']:
                is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                safety = "✓ Safe" if is_safe else f"⚠ {reason}"
                table.add_row(pkg['name'], pkg['current'], pkg['latest'], safety)
            
            self.console.print(table)
        else:
            print("\nOutdated Homebrew Packages:")
            for pkg in info['outdated_packages']:
                is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                print(f"  {pkg['name']}: {pkg['current']} -> {pkg['latest']} ({reason})")
        
        # Ask user if they want to proceed
        if not self.confirm("\nUpgrade Homebrew packages?"):
            return
        
        # Upgrade safe packages automatically (patch updates only)
        safe_packages = [
            pkg['name'] for pkg in info['outdated_packages']
            if self.is_safe_upgrade(pkg['current'], pkg['latest'])[0]
        ]
        
        if safe_packages:
            self.print(f"\n[bold]Upgrading {len(safe_packages)} safe package(s)...[/bold]")
            for pkg in safe_packages:
                self.log(f"Upgrading {pkg}...")
                code, _, _ = self.run_command(f"brew upgrade {pkg}")
                if code == 0:
                    self.print(f"[green]✓[/green] Upgraded {pkg}")
                else:
                    self.print(f"[red]✗[/red] Failed to upgrade {pkg}")
        
        # Handle packages requiring manual review (minor/major updates)
        unsafe_packages = [
            pkg for pkg in info['outdated_packages']
            if not self.is_safe_upgrade(pkg['current'], pkg['latest'])[0]
        ]
        
        if unsafe_packages:
            self.print(f"\n[yellow]⚠ {len(unsafe_packages)} package(s) require manual review[/yellow]")
            for pkg in unsafe_packages:
                is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                self.print(f"  {pkg['name']}: {reason}")
                if self.confirm(f"  Upgrade {pkg['name']} anyway?"):
                    code, _, _ = self.run_command(f"brew upgrade {pkg['name']}")
                    if code == 0:
                        self.print(f"[green]✓[/green] Upgraded {pkg['name']}")
        
        # Cleanup old versions and cache
        if self.confirm("\nRun brew cleanup?"):
            self.print("\n[bold]Cleaning up Homebrew...[/bold]")
            self.run_command("brew cleanup --prune=all -s")
            self.print("[green]✓[/green] Cleanup complete")
    
    # ==================== CONDA ====================
    
    def check_conda(self) -> Dict:
        """
        Check Conda package manager version.
        
        Process:
        1. Get current conda version
        2. Check for available updates (dry-run)
        3. Save results to snapshot
        
        Returns:
            Dictionary containing:
            - current: Current conda version
            - latest: Latest available conda version
            
        Note:
            This checks conda itself, not Python or other packages.
        """
        self.print("\n[bold cyan]Checking Conda...[/bold cyan]")
        
        # Get current conda version
        code, version, _ = self.run_command("conda --version")
        current_version = version.split()[1] if code == 0 else "unknown"
        
        # Check for available updates using dry-run
        code, output, _ = self.run_command("conda update -n base -c defaults conda --dry-run --json")
        latest_version = current_version
        
        if code == 0 and output:
            try:
                data = json.loads(output)
                # Look for conda in the LINK actions
                for action in data.get('actions', {}).get('LINK', []):
                    if action.get('name') == 'conda':
                        latest_version = action.get('version', current_version)
                        break
            except:
                pass
        
        # Store results
        info = {
            'current': current_version,
            'latest': latest_version
        }
        
        self.snapshot['conda'] = info
        
        # Display status
        if current_version == latest_version:
            self.print(f"[green]✓ Conda {current_version} (up to date)[/green]")
        else:
            self.print(f"Current: {current_version} → Latest: {latest_version}")
        
        return info
    
    def upgrade_conda(self):
        """
        Upgrade Conda package manager.
        
        Process:
        1. Check current vs. latest version
        2. Evaluate upgrade safety
        3. Prompt user if upgrade is not a patch update
        4. Execute upgrade if approved
        5. Run conda cleanup if user confirms
        
        Safety:
        - Patch updates: Auto-approved
        - Minor/major updates: Require confirmation
        
        Note:
            This only upgrades conda itself in the base environment.
            Other conda environments are not affected.
        """
        info = self.check_conda()
        
        if info['current'] == info['latest']:
            return
        
        # Evaluate upgrade safety
        is_safe, reason = self.is_safe_upgrade(info['current'], info['latest'])
        
        self.print(f"\nUpgrade available: {info['current']} → {info['latest']}")
        self.print(f"Safety: {reason}")
        
        # Prompt if upgrade is not safe (not a patch update)
        if not is_safe and not self.confirm(f"\n{reason}. Upgrade anyway?"):
            return
        
        # Execute upgrade if safe or user confirmed
        if is_safe or self.confirm("\nProceed with conda upgrade?"):
            self.print("\n[bold]Upgrading Conda...[/bold]")
            code, _, _ = self.run_command("conda update -n base -c defaults conda -y")
            
            if code == 0:
                self.print("[green]✓[/green] Conda upgraded successfully")
                
                # Offer to clean up old packages and cache
                if self.confirm("\nRun conda cleanup?"):
                    self.print("\n[bold]Cleaning up Conda...[/bold]")
                    self.run_command("conda clean --all --yes")
                    self.print("[green]✓[/green] Cleanup complete")
            else:
                self.print("[red]✗[/red] Conda upgrade failed")
    
    # ==================== PYTHON ====================
    
    def detect_python_source(self) -> str:
        """
        Detect which package manager is managing the active Python.
        
        Returns:
            "conda": Python is from Conda
            "homebrew": Python is from Homebrew
            "system": Python is system/other installation
            "unknown": Could not determine source
            
        Note:
            This checks the Python in the current PATH.
        """
        code, python_path, _ = self.run_command("which python")
        
        if code != 0:
            return "unknown"
        
        # Check if Python is from Conda
        if "conda" in python_path.lower() or "anaconda" in python_path.lower() or "miniconda" in python_path.lower():
            return "conda"
        
        # Check if Python is from Homebrew
        if "/opt/homebrew" in python_path or "/usr/local/Cellar" in python_path:
            return "homebrew"
        
        # Check if it's the system Python
        if python_path.startswith("/usr/bin") or python_path.startswith("/System"):
            return "system"
        
        # Could be pyenv, asdf, or another version manager
        return "unknown"
    
    def check_python(self) -> Dict:
        """
        Check Python version and detect its source (Conda/Homebrew/System).
        
        Process:
        1. Detect Python source (Conda, Homebrew, or System)
        2. Get current Python version
        3. Check for available updates based on source
        4. Save results to snapshot
        
        Returns:
            Dictionary containing:
            - current: Current Python version
            - latest: Latest Python version available
            - source: Where Python is installed from
            - manageable: Whether this tool can upgrade it
            
        Note:
            - Conda Python: Can be upgraded via conda
            - Homebrew Python: Can be upgraded via brew
            - System Python: Should NOT be upgraded (macOS system Python)
            - Other: Not managed by this tool
        """
        self.print("\n[bold cyan]Checking Python...[/bold cyan]")
        
        # Detect Python source
        python_source = self.detect_python_source()
        
        # Get current Python version
        code, version, _ = self.run_command("python --version")
        current_version = version.split()[1] if code == 0 else "unknown"
        
        # Get Python path for display
        code, python_path, _ = self.run_command("which python")
        python_path = python_path if code == 0 else "unknown"
        
        latest_version = current_version
        manageable = False
        
        # Check for updates based on source
        if python_source == "conda":
            # Search conda for available Python versions
            code, output, _ = self.run_command("conda search python --json")
            if code == 0 and output:
                try:
                    data = json.loads(output)
                    versions = [v['version'] for v in data.get('python', [])]
                    if versions:
                        latest_version = max(versions, key=lambda v: self.parse_version(v))
                    manageable = True
                except:
                    pass
        
        elif python_source == "homebrew":
            # Check Homebrew for Python updates
            code, output, _ = self.run_command("brew info python --json")
            if code == 0 and output:
                try:
                    data = json.loads(output)
                    if data and len(data) > 0:
                        versions = data[0].get('versions', {})
                        latest_version = versions.get('stable', current_version)
                        manageable = True
                except:
                    pass
        
        # Store results
        info = {
            'current': current_version,
            'latest': latest_version,
            'source': python_source,
            'path': python_path,
            'manageable': manageable
        }
        
        self.snapshot['python'] = info
        
        # Display status with source information
        source_display = {
            'conda': '[cyan]Conda[/cyan]',
            'homebrew': '[yellow]Homebrew[/yellow]',
            'system': '[red]System (not upgradeable)[/red]',
            'unknown': '[dim]Unknown source[/dim]'
        }.get(python_source, python_source)
        
        self.print(f"Python {current_version} from {source_display}")
        self.print(f"Path: [dim]{python_path}[/dim]")
        
        if not manageable:
            if python_source == "system":
                self.print("[yellow]⚠ System Python should not be modified[/yellow]")
            else:
                self.print("[yellow]⚠ Python not managed by Conda or Homebrew[/yellow]")
        elif current_version == latest_version:
            self.print(f"[green]✓ Up to date[/green]")
        else:
            self.print(f"Update available: {current_version} → {latest_version}")
        
        return info
    
    def upgrade_python(self):
        """
        Upgrade Python via its package manager (Conda or Homebrew).
        
        Process:
        1. Detect Python source (Conda, Homebrew, System, or Other)
        2. Check current vs. latest Python version
        3. Evaluate upgrade safety
        4. Strongly warn about major/minor version changes
        5. Execute upgrade using appropriate package manager
        
        Safety:
        - Patch updates: Auto-approved (e.g., 3.12.11 → 3.12.12)
        - Minor updates: Require confirmation (e.g., 3.11.x → 3.12.x)
        - Major updates: Strongly discouraged (e.g., 3.x → 4.x)
        
        ⚠️  WARNING:
            Python version upgrades can break existing projects!
            - Check project compatibility before upgrading
            - Test all projects after upgrade
            - For Conda: Consider using conda environments instead
            - For Homebrew: Projects may need virtualenv recreation
        
        Supported Sources:
        - Conda: Upgraded via `conda update python`
        - Homebrew: Upgraded via `brew upgrade python@3.x`
        - System: NOT upgraded (macOS system Python)
        - Other: NOT supported (pyenv, asdf, manual installs, etc.)
        """
        info = self.check_python()
        
        # Check if Python is manageable
        if not info.get('manageable', False):
            source = info.get('source', 'unknown')
            if source == 'system':
                self.print("\n[red]✗[/red] Cannot upgrade system Python")
                self.print("[yellow]System Python is managed by macOS and should not be modified.[/yellow]")
                self.print("[yellow]Consider installing Python via Homebrew or Conda instead.[/yellow]")
            else:
                self.print(f"\n[red]✗[/red] Python from '{source}' is not managed by this tool")
                self.print("[yellow]This tool only supports Python from Conda or Homebrew.[/yellow]")
            return
        
        if info['current'] == info['latest']:
            return
        
        # Evaluate upgrade safety
        is_safe, reason = self.is_safe_upgrade(info['current'], info['latest'])
        
        self.print(f"\nUpgrade available: {info['current']} → {info['latest']}")
        self.print(f"Safety: {reason}")
        self.print(f"Source: {info['source']}")
        
        # Show warning for non-patch updates
        if not is_safe:
            self.print(f"[yellow]⚠ Python upgrade skipped: {reason}[/yellow]")
            if not self.confirm("\nUpgrade anyway?"):
                return
        
        # Final confirmation before upgrade
        if self.confirm("\nProceed with Python upgrade?"):
            self.print("\n[bold]Upgrading Python...[/bold]")
            
            # Execute upgrade based on source
            if info['source'] == 'conda':
                code, _, _ = self.run_command("conda update python -y")
            elif info['source'] == 'homebrew':
                # Homebrew Python is typically python@3.x
                # Try to upgrade python3 formula
                code, _, _ = self.run_command("brew upgrade python@3 || brew upgrade python3 || brew upgrade python")
            else:
                self.print(f"[red]✗[/red] Unknown Python source: {info['source']}")
                return
            
            if code == 0:
                self.print("[green]✓[/green] Python upgraded successfully")
                self.print("\n[yellow]⚠ IMPORTANT:[/yellow]")
                if info['source'] == 'conda':
                    self.print("  - Test your conda environments")
                    self.print("  - Reinstall packages if needed")
                elif info['source'] == 'homebrew':
                    self.print("  - Recreate virtual environments (venv)")
                    self.print("  - Reinstall packages with pip if needed")
            else:
                self.print("[red]✗[/red] Python upgrade failed")
    
    # ==================== NPM ====================
    
    def check_npm(self) -> Dict:
        """
        Check npm version and global packages.
        
        Process:
        1. Get current npm version
        2. Check latest npm version available
        3. List outdated global packages
        4. Save results to snapshot
        
        Returns:
            Dictionary containing:
            - current: Current npm version
            - latest: Latest npm version
            - outdated_count: Number of outdated global packages
            - outdated_packages: List of outdated package details
            
        Note:
            This only checks global npm packages (-g).
            Project-local packages are not checked.
        """
        self.print("\n[bold cyan]Checking npm...[/bold cyan]")
        
        # Get current npm version
        code, version, _ = self.run_command("npm --version")
        current_version = version if code == 0 else "unknown"
        
        # Get latest npm version from registry
        code, latest, _ = self.run_command("npm view npm version")
        latest_version = latest if code == 0 else current_version
        
        # Check for outdated global packages
        code, output, _ = self.run_command("npm outdated -g --json")
        outdated_packages = []
        
        if code == 0 and output:
            try:
                data = json.loads(output)
                for name, details in data.items():
                    outdated_packages.append({
                        'name': name,
                        'current': details.get('current', 'unknown'),
                        'latest': details.get('latest', 'unknown')
                    })
            except:
                pass
        
        # Store results
        info = {
            'current': current_version,
            'latest': latest_version,
            'outdated_count': len(outdated_packages),
            'outdated_packages': outdated_packages
        }
        
        self.snapshot['npm'] = info
        
        # Display summary
        self.print(f"npm: {current_version} → Latest: {latest_version}")
        
        if outdated_packages:
            self.print(f"Found {len(outdated_packages)} outdated global package(s)")
        else:
            self.print("[green]✓ All global npm packages up to date[/green]")
        
        return info
    
    def upgrade_npm(self):
        """
        Upgrade npm and global packages.
        
        Process:
        1. Display table of outdated global packages
        2. Upgrade safe (patch) packages automatically
        3. Prompt for unsafe (minor/major) packages
        4. Upgrade npm itself last (best practice)
        5. Verify npm cache if user confirms
        
        Safety:
        - Patch updates: Upgraded automatically
        - Minor/major updates: Require user confirmation
        
        Note:
            npm itself is upgraded LAST to avoid potential issues
            with upgrading other packages.
        """
        info = self.check_npm()
        
        # Handle global package upgrades first
        if info['outdated_count'] > 0:
            # Display table of outdated packages
            if self.console:
                table = Table(title="Outdated npm Global Packages")
                table.add_column("Package", style="cyan")
                table.add_column("Current", style="yellow")
                table.add_column("Latest", style="green")
                table.add_column("Safety", style="magenta")
                
                for pkg in info['outdated_packages']:
                    is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                    safety = "✓ Safe" if is_safe else f"⚠ {reason}"
                    table.add_row(pkg['name'], pkg['current'], pkg['latest'], safety)
                
                self.console.print(table)
            else:
                print("\nOutdated npm Global Packages:")
                for pkg in info['outdated_packages']:
                    is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                    print(f"  {pkg['name']}: {pkg['current']} -> {pkg['latest']} ({reason})")
            
            if self.confirm("\nUpgrade global packages?"):
                # Upgrade safe packages (patch updates)
                safe_packages = [
                    pkg['name'] for pkg in info['outdated_packages']
                    if self.is_safe_upgrade(pkg['current'], pkg['latest'])[0]
                ]
                
                if safe_packages:
                    self.print(f"\n[bold]Upgrading {len(safe_packages)} safe package(s)...[/bold]")
                    for pkg in safe_packages:
                        self.log(f"Upgrading {pkg}...")
                        code, _, _ = self.run_command(f"npm install -g {pkg}@latest")
                        if code == 0:
                            self.print(f"[green]✓[/green] Upgraded {pkg}")
                
                # Handle packages requiring manual review
                unsafe_packages = [
                    pkg for pkg in info['outdated_packages']
                    if not self.is_safe_upgrade(pkg['current'], pkg['latest'])[0]
                ]
                
                if unsafe_packages:
                    self.print(f"\n[yellow]⚠ {len(unsafe_packages)} package(s) require manual review[/yellow]")
                    for pkg in unsafe_packages:
                        is_safe, reason = self.is_safe_upgrade(pkg['current'], pkg['latest'])
                        self.print(f"  {pkg['name']}: {reason}")
                        if self.confirm(f"  Upgrade {pkg['name']} anyway?"):
                            code, _, _ = self.run_command(f"npm install -g {pkg['name']}@latest")
                            if code == 0:
                                self.print(f"[green]✓[/green] Upgraded {pkg['name']}")
        
        # Upgrade npm itself LAST (best practice)
        if info['current'] != info['latest']:
            is_safe, reason = self.is_safe_upgrade(info['current'], info['latest'])
            
            self.print(f"\n[bold]npm upgrade available:[/bold] {info['current']} → {info['latest']}")
            self.print(f"Safety: {reason}")
            
            # Prompt if not a safe upgrade
            if not is_safe and not self.confirm(f"\n{reason}. Upgrade anyway?"):
                return
            
            # Execute npm upgrade
            if is_safe or self.confirm("\nUpgrade npm itself?"):
                self.print("\n[bold]Upgrading npm...[/bold]")
                code, _, _ = self.run_command("npm install -g npm@latest")
                
                if code == 0:
                    self.print("[green]✓[/green] npm upgraded successfully")
                else:
                    self.print("[red]✗[/red] npm upgrade failed")
        
        # Verify and clean npm cache
        if self.confirm("\nRun npm cache verify?"):
            self.print("\n[bold]Verifying npm cache...[/bold]")
            self.run_command("npm cache verify")
            self.print("[green]✓[/green] Cache verified")
    
    # ==================== MAIN MENU ====================
    
    def show_menu(self):
        """
        Display the main interactive menu.
        
        Menu Options:
        1. Upgrade Homebrew - Updates Homebrew packages
        2. Upgrade Conda - Updates conda package manager
        3. Upgrade Python - Updates Python via conda
        4. Upgrade npm - Updates npm and global packages
        5. Check All - Shows versions without upgrading
        6. Upgrade All - Runs all upgrades in sequence
        0. Exit - Quits the program
        
        Returns:
            User's menu selection as string
        """
        self.print_panel(
            "[bold]macOS Dev Toolkit Manager[/bold]\n\n"
            "1. Upgrade Homebrew\n"
            "2. Upgrade Conda\n"
            "3. Upgrade Python\n"
            "4. Upgrade npm\n"
            "5. Check All (no upgrades)\n"
            "6. Upgrade All\n"
            "0. Exit",
            title="Main Menu"
        )
        
        if self.console:
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6"])
        else:
            choice = input("Select option [0-6]: ").strip()
        
        return choice
    
    def run(self):
        """
        Main program loop.
        
        Displays welcome message with log locations,
        then shows interactive menu until user exits.
        
        After each operation, a snapshot is saved automatically.
        """
        self.print_panel(
            "[bold cyan]macOS Dev Toolkit Manager[/bold cyan]\n\n"
            f"Script: safe_update.py v1.2.0\n"
            f"Log file: {self.log_file}\n"
            f"Snapshot: {self.snapshot_file}\n\n"
            "This tool will help you safely upgrade your development packages.",
            title="Welcome"
        )
        
        # Main menu loop
        while True:
            choice = self.show_menu()
            
            if choice == "0":
                self.print("\n[bold]Goodbye![/bold]")
                break
            elif choice == "1":
                self.upgrade_homebrew()
            elif choice == "2":
                self.upgrade_conda()
            elif choice == "3":
                self.upgrade_python()
            elif choice == "4":
                self.upgrade_npm()
            elif choice == "5":
                # Check all without upgrading
                self.check_homebrew()
                self.check_conda()
                self.check_python()
                self.check_npm()
            elif choice == "6":
                # Upgrade all in sequence
                self.save_snapshot()
                self.upgrade_homebrew()
                self.upgrade_conda()
                self.upgrade_python()
                self.upgrade_npm()
                self.print("\n[bold green]✓ All upgrades complete![/bold green]")
            
            # Save snapshot after each operation
            if choice != "0":
                self.save_snapshot()
                input("\nPress Enter to continue...")


if __name__ == "__main__":
    """
    Main entry point.
    
    Handles:
    - Normal execution
    - Keyboard interrupts (Ctrl+C)
    - Unexpected exceptions
    """
    try:
        manager = SystemUpgradeManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
