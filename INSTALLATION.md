# CORE Installation Guide

This document provides installation and first-run instructions for CORE (Collection Object Record Editor) on macOS, Windows, and Linux.

## Table of Contents

- [macOS Installation (DMG)](#macos-installation-dmg)
- [Windows Installation (ZIP)](#windows-installation-zip)
- [Linux and macOS Installation (Source)](#linux-and-macos-installation-source)
- [Prerequisites](#prerequisites)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)
- [Support](#support)

## macOS Installation (DMG)

CORE for macOS can be distributed as a DMG package containing CORE.app.

### Prerequisites

- macOS 12 (Monterey) or later
- Python 3.8 or later installed
  - Download: https://python.org/downloads
  - Or via Homebrew: brew install python
  - Verify: python3 --version

### Installation Steps

1. Download the DMG
   - Download CORE_vX.Y.dmg from your distribution source.

2. Open the DMG
   - Double-click the downloaded DMG file.

3. Install CORE.app
   - Drag CORE.app to Applications (or another folder you control).

4. Eject the DMG
   - Eject the mounted volume from Finder.

### First Launch on macOS

Because CORE.app is unsigned, Gatekeeper may block first launch.

1. Right-click CORE.app and choose Open.
2. Click Open in the confirmation dialog.
3. A Terminal window opens and runs CORE setup.
4. On first run, CORE creates .venv and installs dependencies.
5. The CORE window opens when setup is complete.

Keep the Terminal window open while the app is running.

## Windows Installation (ZIP)

CORE for Windows can be distributed as a ZIP archive.

### Prerequisites

- Windows 10 or Windows 11
- Python 3.8 or later installed
  - Download: https://python.org/downloads
  - During install, enable "Add Python to PATH"
  - Verify in Command Prompt: python --version

### Installation Steps

1. Download the ZIP
   - Download CORE_vX.Y_Windows.zip.

2. Extract the archive
   - Right-click the ZIP and choose Extract All.
   - Extract to a convenient location.

3. Launch CORE
   - Open the extracted CORE folder.
   - Run scripts/run.bat (or run.bat if included at the package root).

### First Launch on Windows

1. A Command Prompt window opens.
2. CORE creates .venv on first run.
3. Dependencies are installed automatically.
4. The CORE app window opens when ready.

Keep the console window open while CORE is running.

## Linux and macOS Installation (Source)

Use this method when running CORE directly from a cloned repository.

### Prerequisites

- Python 3.8 or later
- Git (if cloning from a repository)

### Installation Steps

1. Clone the repository

```bash
git clone https://github.com/Digital-Grinnell/CORE.git
cd CORE
```

2. Launch CORE

```bash
./run.sh
```

The launcher script will:
- create .venv if needed
- upgrade pip
- install dependencies from python_requirements.txt
- start CORE

## Prerequisites

### Python

CORE requires Python 3.8 or later.

```bash
# macOS/Linux
python3 --version

# Windows
python --version
```

### Python Dependencies

CORE installs required dependencies automatically on first launch:

- flet==0.25.2
- flet-desktop==0.25.2
- cryptography>=41.0.0

You usually do not need to install these manually if you use run.sh or scripts/run.bat.

## Troubleshooting

### macOS and Linux

#### ./run.sh permission denied

```bash
chmod +x run.sh scripts/run.sh
./run.sh
```

#### python3 not found

Install Python 3 and verify:

```bash
python3 --version
```

### Windows

#### python is not recognized

- Reinstall Python from https://python.org/downloads
- Enable "Add Python to PATH"
- Reopen Command Prompt
- Verify: python --version

#### Dependency install fails

```bat
python -m pip install --upgrade pip
scripts\run.bat
```

#### Virtual environment appears corrupted

```bat
rmdir /s .venv
scripts\run.bat
```

### Common Issues (All Platforms)

#### CORE closes immediately

- Re-run from terminal/console and review error output.
- Check logs in ~/CORE-data/logfiles/.
- If needed, clear persisted UI state by removing ~/CORE-data/persistent.json.

#### CORE-settings.json behavior seems wrong

- Ensure CORE-settings.json is in the same folder as app.py.
- Confirm field names match CSV headers.
- Restart CORE after changing settings if behavior appears stale.

## Uninstallation

### macOS

If installed as an app, remove CORE.app from Applications (or wherever installed).

If running from source, delete the project folder.

Optional user data cleanup:

```bash
rm -rf ~/CORE-data
```

### Windows

1. Delete the extracted CORE folder (or uninstall location).
2. Optional: remove user data folder at C:\Users\YourName\CORE-data.
3. Remove any Desktop shortcut you created.

### Linux

```bash
# Remove source checkout
rm -rf /path/to/CORE

# Optional user data cleanup
rm -rf ~/CORE-data
```

## Support

- Overview and usage: README.md
- Quick workflow guide: QUICKSTART.md
- Runtime source: app.py

Logs for troubleshooting:
- ~/CORE-data/logfiles/core_YYYYMMDD_HHMMSS.log

Last updated: 2026-06-26
