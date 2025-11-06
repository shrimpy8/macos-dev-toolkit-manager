# Changelog
## macOS Dev Toolkit Manager (formerly System Upgrade Manager)

All notable changes to this project will be documented in this file.

## [1.2.0] - 2025-11-06

### Changed - Project Renamed
- **Project folder**: `system-upgrade-manager` → `macos-dev-toolkit-manager`
- **Script name**: `system_upgrade.py` → `safe_update.py`
- More descriptive and purposeful names
- Emphasizes macOS development toolkit management
- Script name emphasizes safety focus
- All documentation updated with new names

## [1.1.0] - 2025-11-06

### Added - Python Source Detection
- **Automatic Python source detection** - The script now automatically detects whether Python is from:
  - ✅ **Conda** (Anaconda/Miniconda) - Upgraded via `conda update python`
  - ✅ **Homebrew** - Upgraded via `brew upgrade python@3`
  - ⚠️ **System** (macOS) - Protected, will NOT be upgraded
  - ❌ **Other** (pyenv, asdf, manual) - Not supported, clear warning shown

### Changed
- `check_python()` now returns additional fields:
  - `source`: Where Python is installed from
  - `path`: Full path to Python executable
  - `manageable`: Boolean indicating if this tool can upgrade it
- `upgrade_python()` now intelligently upgrades based on detected source
- Enhanced output shows Python source and path for transparency

### Enhanced
- **Better error messages** when Python can't be upgraded
- **Post-upgrade warnings** specific to each Python source:
  - Conda: Warns to test conda environments
  - Homebrew: Warns to recreate virtual environments
- **Safety protection** for system Python - explicitly prevents modification

### Documentation
- Updated README.md with Python source detection details
- Updated DISCLAIMER.md with Python source information
- Updated QUICKSTART.md with Python detection examples
- Added comprehensive inline documentation in the script

### Technical Details

#### Detection Logic
```python
def detect_python_source() -> str:
    # Checks Python path to determine source:
    # - Contains "conda/anaconda/miniconda" → conda
    # - Contains "/opt/homebrew" or "/usr/local/Cellar" → homebrew
    # - Starts with "/usr/bin" or "/System" → system
    # - Otherwise → unknown
```

#### Upgrade Commands
- **Conda Python**: `conda update python -y`
- **Homebrew Python**: `brew upgrade python@3 || brew upgrade python3 || brew upgrade python`
- **System Python**: No command (blocked)

#### Safety Features
- System Python is never modified (prevents breaking macOS)
- Clear warnings for non-manageable Python installations
- Shows Python path and source before any upgrade
- Post-upgrade reminders specific to each source

## [1.0.0] - 2025-11-05

### Initial Release
- Interactive menu system for package manager upgrades
- Support for Homebrew, Conda, Python (Conda only), and npm
- Safety rules: patch auto-approved, minor/major require confirmation
- Pre-upgrade snapshots saved to ~/upgrade-logs/
- Detailed logging with timestamps
- Rich UI with tables and panels (optional)
- Comprehensive documentation (README, QUICKSTART, DISCLAIMER)
- MIT License with additional disclaimers

---

## Upgrade Guide

### From 1.0.0 to 1.1.0

No action required! The script will automatically detect your Python source.

**What to expect:**
1. Run the script as usual
2. When checking Python (Option 3 or 5), you'll see:
   ```
   Python 3.12.12 from Conda
   Path: /opt/anaconda3/bin/python
   ✓ Up to date
   ```
3. If upgrading Python, the correct package manager is used automatically

**Benefits:**
- If you have Homebrew Python, it will now be detected and upgraded correctly
- If you have system Python, it will be protected from accidental modification
- Clearer visibility into which Python installation is being managed

**No Breaking Changes:**
- Existing Conda Python workflows unchanged
- All other features work exactly the same
- Snapshots and logs continue to work as before

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards compatible)
- **PATCH** version: Bug fixes (backwards compatible)

Format: `MAJOR.MINOR.PATCH` (e.g., 1.1.0)
