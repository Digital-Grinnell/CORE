# CORE - Collection Object Record Editor

CORE is a Flet desktop application for editing one object record at a time from a project’s CollectionBuilder metadata CSV file. It reads the CSV headers to build a record-specific form, lets the user choose a single row, and saves the edited row back to the same file.

## What It Does

- Browse directly to a metadata CSV file
- Load the CSV headers and row data into a generated form
- Select a single record from a dropdown list
- Edit the current row in place
- Save the updated row back to the original metadata CSV
- Create a timestamped backup on each save inside `.CORE-working-directory` next to the CSV file
- Remember the last CSV file and selected record
- Apply field behavior overrides from `CORE-settings.json` (`hidden`, `disabled`, and slash-combined values)
- Use **Unhide/Enable All** as a toggle to temporarily ignore `hidden` and `disabled` settings for the active session, then toggle back to restore them

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

- [INSTALLATION.md](INSTALLATION.md) - installation and first-run instructions for macOS, Windows, and Linux
- [app.py](app.py) - CORE runtime and CSV editor UI
- [run.sh](run.sh) - root shortcut that forwards to scripts/run.sh
- [scripts/run.sh](scripts/run.sh) - macOS/Linux launcher
- [scripts/run.bat](scripts/run.bat) - Windows launcher
- [scripts/build_dmg.sh](scripts/build_dmg.sh) - macOS packaging script
- [scripts/build_windows_zip.sh](scripts/build_windows_zip.sh) - Windows packaging script
- [python_requirements.txt](python_requirements.txt) - Python dependencies

## Runtime Data

CORE stores its local state in `~/CORE-data/`:

- `persistent.json` - last-used CSV file and selected record
- `logfiles/core_YYYYMMDD_HHMMSS.log` - timestamped application logs

CORE also creates a per-project working folder beside the edited CSV file:

- `.CORE-working-directory/` - timestamped CSV backups and temporary save files

CORE can also read optional field settings from the app folder:

- `CORE-settings.json` - per-field characteristics; keys are CSV field names
- Supported now: `hidden`, `disabled`, and combined strings like `disabled/boolean`
- Any field not listed defaults to editable visible text
- The **Unhide/Enable All** toggle is session-only and does not modify `CORE-settings.json`

## Version History

CORE follows the DART-style version history pattern:

- `VERSION` is the single source of truth for the app version.
- `CHANGELOG.md` tracks release history and unreleased changes.
- The UI reads `VERSION` at startup and displays it in the app title/header.

## Customization Notes

The main behavior lives in [app.py](app.py). If you want to adapt CORE for another metadata workflow, the key extension points are:

- `load_metadata_csv()` - CSV parsing
- `render_record_form()` - dynamic form generation
- `save_metadata_csv()` - write-back behavior

## Development Check

```bash
python3 -m py_compile app.py
```