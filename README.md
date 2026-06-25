# CORE - Collection Object Record Editor

CORE is a Flet desktop application for editing one object record at a time from a project’s CollectionBuilder metadata CSV file. It reads the CSV headers to build a record-specific form, lets the user choose a single row, and saves the edited row back to the same file.

## What It Does

- Open a project folder and auto-detect a likely metadata CSV, or browse directly to the CSV file
- Load the CSV headers and row data into a generated form
- Select a single record from a dropdown list
- Edit the current row in place
- Save the updated row back to the original metadata CSV
- Remember the last project folder, CSV file, and selected record

## Run It

```bash
./run.sh
```

On Windows:

```bat
scripts\\run.bat
```

The launch scripts create a virtual environment, install dependencies, and start the app.

## Requirements

- Python 3.8+
- Flet 0.25.2
- cryptography 41+

## Files of Interest

- [app.py](app.py) - CORE runtime and CSV editor UI
- [run.sh](run.sh) - root shortcut that forwards to scripts/run.sh
- [scripts/run.sh](scripts/run.sh) - macOS/Linux launcher
- [scripts/run.bat](scripts/run.bat) - Windows launcher
- [scripts/build_dmg.sh](scripts/build_dmg.sh) - macOS packaging script
- [scripts/build_windows_zip.sh](scripts/build_windows_zip.sh) - Windows packaging script
- [python_requirements.txt](python_requirements.txt) - Python dependencies

## Runtime Data

CORE stores its local state in `~/CORE-data/`:

- `persistent.json` - last-used folder, CSV, and selected record
- `logfiles/core_YYYYMMDD_HHMMSS.log` - timestamped application logs

## Version History

CORE follows the DART-style version history pattern:

- `VERSION` is the single source of truth for the app version.
- `CHANGELOG.md` tracks release history and unreleased changes.
- The UI reads `VERSION` at startup and displays it in the app title/header.

## Customization Notes

The main behavior lives in [app.py](app.py). If you want to adapt CORE for another metadata workflow, the key extension points are:

- `discover_metadata_csv()` - project folder file discovery
- `load_metadata_csv()` - CSV parsing
- `render_record_form()` - dynamic form generation
- `save_metadata_csv()` - write-back behavior

## Development Check

```bash
python3 -m py_compile app.py
```