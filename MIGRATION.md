# Migration Guide: Project Renamed

## What Changed in v1.2.0

This project has been renamed to better communicate its purpose:

### Old Names ❌
- **Folder**: `system-upgrade-manager`
- **Script**: `system_upgrade.py`

### New Names ✅
- **Folder**: `macos-dev-toolkit-manager`
- **Script**: `safe_update.py`

## Why the Change?

1. **More Descriptive**: "macOS Dev Toolkit Manager" clearly indicates it's for macOS development tools
2. **Professional**: Better name for GitHub/portfolio
3. **Emphasizes Safety**: Script name "safe_update.py" highlights the safety-first approach
4. **SEO-Friendly**: More discoverable for developers searching for macOS update tools

## How to Migrate

### If You Haven't Cloned Yet
Just use the new names:
```bash
git clone <your-repo-url> macos-dev-toolkit-manager
cd macos-dev-toolkit-manager
./safe_update.py
```

### If You Already Have the Old Version

#### Option 1: Rename Your Local Folder
```bash
cd ~/Documents/GitHub
mv system-upgrade-manager macos-dev-toolkit-manager
cd macos-dev-toolkit-manager
```

The script is already renamed to `safe_update.py`, so just use that:
```bash
./safe_update.py
```

#### Option 2: Fresh Clone
```bash
cd ~/Documents/GitHub
rm -rf system-upgrade-manager  # Remove old folder
git clone <your-repo-url> macos-dev-toolkit-manager
cd macos-dev-toolkit-manager
./safe_update.py
```

### Your Logs Are Safe! 📁

Don't worry - your upgrade logs and snapshots are stored in `~/upgrade-logs/` which is **outside** the project folder. They will continue to work regardless of the project rename.

```bash
# Your logs are still here:
ls -lh ~/upgrade-logs/
```

## What Stayed the Same

- ✅ All functionality unchanged
- ✅ Log files in `~/upgrade-logs/` still work
- ✅ Same commands and menu options
- ✅ All safety features intact
- ✅ Configuration and behavior identical

## Updated References

All documentation has been updated:
- ✅ README.md
- ✅ QUICKSTART.md
- ✅ DISCLAIMER.md
- ✅ CHANGELOG.md
- ✅ LICENSE
- ✅ Script header and UI text

## Quick Reference Card

### Before (v1.0.0 - v1.1.0)
```bash
cd system-upgrade-manager
./system_upgrade.py
```

### After (v1.2.0+)
```bash
cd macos-dev-toolkit-manager
./safe_update.py
```

## Troubleshooting

### "Command not found: safe_update.py"
Make sure you're in the right folder:
```bash
pwd  # Should show: .../macos-dev-toolkit-manager
ls   # Should show: safe_update.py
```

If you see `system_upgrade.py` instead, you're in the old folder. Rename it or clone fresh.

### Old bookmarks/aliases
Update any bookmarks, aliases, or shortcuts you created:

**Bash/Zsh alias (old):**
```bash
alias update='~/Documents/GitHub/system-upgrade-manager/system_upgrade.py'
```

**Bash/Zsh alias (new):**
```bash
alias update='~/Documents/GitHub/macos-dev-toolkit-manager/safe_update.py'
```

### Scripts that reference the old name
If you have scripts or automation that reference the old names, update them:

```bash
# Old
/path/to/system-upgrade-manager/system_upgrade.py

# New
/path/to/macos-dev-toolkit-manager/safe_update.py
```

## Questions?

The rename is purely cosmetic - all functionality is identical. If you have any issues:

1. Check you're using `safe_update.py` (not `system_upgrade.py`)
2. Check you're in the `macos-dev-toolkit-manager` folder
3. Your logs in `~/upgrade-logs/` are unaffected
4. All commands and options work exactly the same

---

**TL;DR**: Just rename your local folder to `macos-dev-toolkit-manager` and run `./safe_update.py` instead of `./system_upgrade.py`. Everything else stays the same! 🚀
