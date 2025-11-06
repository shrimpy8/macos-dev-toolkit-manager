# Quick Start Guide
## macOS Dev Toolkit Manager

**Script:** `safe_update.py` - Safe package manager updates for macOS developers

## First Time Setup

### 1. Read the Disclaimer
**⚠️ IMPORTANT:** Before using this tool, read [DISCLAIMER.md](DISCLAIMER.md) to understand the risks.

### 2. Install Dependencies (Optional but Recommended)

```bash
pip install rich
```

The `rich` library provides a better UI with colors and tables. The script will work without it, but the experience is better with it.

### 3. Make Sure You Have the Tools

This script can manage:
- **Homebrew** (install from [brew.sh](https://brew.sh))
- **Conda** (install from [conda.io](https://conda.io))
- **Python** (automatically detects if from Conda or Homebrew)
  - ✅ Conda Python: Fully supported
  - ✅ Homebrew Python: Fully supported
  - ⚠️ System Python: Protected (will not upgrade)
  - ❌ Other (pyenv, asdf, etc.): Not supported
- **npm** (comes with Node.js from [nodejs.org](https://nodejs.org))

You don't need all of them - the script will skip any that aren't installed.

## Running the Script

### Option 1: Direct Execution

```bash
cd /path/to/macos-dev-toolkit-manager
./safe_update.py
```

### Option 2: With Python

```bash
cd /path/to/macos-dev-toolkit-manager
python safe_update.py
```

## First Run - Recommended Steps

### Step 1: Check Everything (Don't Upgrade Yet)

1. Run the script
2. Select option **5** (Check All - no upgrades)
3. Review what's installed and what's outdated
4. Exit (option 0)

### Step 2: Backup Your Work

```bash
# Commit and push all your code
cd ~/your-project
git add .
git commit -m "Backup before system upgrades"
git push
```

### Step 3: Run Selective Upgrades

Start with one package manager:

```bash
./safe_update.py
# Select option 1 (Homebrew) or 2 (Conda) or 4 (npm)
```

Watch the output carefully:
- ✅ Green "Safe" means patch updates (auto-approved)
- ⚠️ Yellow means minor/major updates (you'll be asked)
- Read each prompt before confirming

### Step 4: Test Your Environment

After each upgrade:
```bash
# Test your projects
cd ~/your-project
python your_script.py  # or npm start, etc.

# Run your tests if you have them
pytest  # or npm test, etc.
```

## Daily Usage

Once you're comfortable:

### Quick Check (No Changes)
```bash
./safe_update.py
# Option 5: Check All
```

### Safe Upgrades Only
```bash
./safe_update.py
# Option 6: Upgrade All
# Only confirm "safe" patches, skip major/minor updates
```

### Full Maintenance
```bash
./safe_update.py
# Option 6: Upgrade All
# Review and confirm minor/major updates as needed
```

## Understanding the Output

### Menu Options
- **Option 1-4**: Upgrade individual tools
- **Option 5**: Check versions only (safe to run anytime)
- **Option 6**: Upgrade everything in sequence
- **Option 0**: Exit

### Safety Indicators
| Symbol | Meaning | Action |
|--------|---------|--------|
| ✅ | Patch update (3.12.11 → 3.12.12) | Auto-approved |
| ⚠️ | Minor update (10.x → 11.x) | Asks for confirmation |
| 🛑 | Major update (3.x → 4.x) | Requires careful review |

### Log Files
Every run creates logs in `~/upgrade-logs/`:
```
~/upgrade-logs/
├── upgrade_20250605_143022.log     # Command log
└── snapshot_20250605_143022.json   # Version snapshot
```

## Troubleshooting

### "Command not found"
Make sure the script is executable:
```bash
chmod +x safe_update.py
```

### "rich library not found"
Install it for a better experience:
```bash
pip install rich
```
Or continue without it - the script will work in plain text mode.

### Something Broke After Upgrade
1. Check the snapshot: `cat ~/upgrade-logs/snapshot_TIMESTAMP.json`
2. Find the old version
3. Reinstall it:
   ```bash
   brew install package@version
   conda install package=version
   npm install -g package@version
   ```

### Conda Says "Cannot Remove Dependencies"
This is a known conda issue. Try:
```bash
conda update -n base conda --force-reinstall
```

## Tips

### ✅ DO
- Run "Check All" (option 5) before upgrading
- Backup your work first
- Read what will be upgraded
- Test after upgrading
- Keep snapshots for 30 days

### ❌ DON'T
- Upgrade right before deadlines
- Accept all upgrades blindly
- Forget to test afterward
- Run on production systems
- Upgrade everything at once (first time)

## Getting Help

### Check the Logs
```bash
# View the latest log
ls -lt ~/upgrade-logs/ | head -n 5
cat ~/upgrade-logs/upgrade_TIMESTAMP.log
```

### Check the Snapshot
```bash
# View the latest snapshot
cat ~/upgrade-logs/snapshot_TIMESTAMP.json
```

### Rollback Example
```bash
# If Python broke, reinstall old version
conda install python=3.12.11

# If an npm package broke
npm install -g package@old-version

# If Homebrew package broke
brew install package@old-version
```

## Example Session

```
$ ./safe_update.py

╭─────────────────── Welcome ───────────────────╮
│ System Upgrade Manager                        │
│                                               │
│ Log file: ~/upgrade-logs/upgrade_...log      │
│ Snapshot: ~/upgrade-logs/snapshot_...json    │
│                                               │
│ This tool will help you safely upgrade       │
│ your system packages.                         │
╰───────────────────────────────────────────────╯

╭─────────────────── Main Menu ─────────────────╮
│ 1. Upgrade Homebrew                           │
│ 2. Upgrade Conda                              │
│ 3. Upgrade Python                             │
│ 4. Upgrade npm                                │
│ 5. Check All (no upgrades)                    │
│ 6. Upgrade All                                │
│ 0. Exit                                       │
╰───────────────────────────────────────────────╯

Select option: 5

✓ Checking Homebrew...
✓ All packages up to date

✓ Checking Conda...
✓ Conda 25.9.1 (up to date)

✓ Checking Python...
✓ Python 3.12.12 (up to date)

✓ Checking npm...
✓ All global packages up to date

✓ Snapshot saved to: ~/upgrade-logs/snapshot_...json
```

## What's Next?

- Read the full [README.md](README.md) for detailed information
- Review [DISCLAIMER.md](DISCLAIMER.md) for safety information
- Bookmark `~/upgrade-logs/` to check logs after upgrades
- Set a reminder to run this monthly

---

**Happy upgrading! Remember to backup first! 🚀**
