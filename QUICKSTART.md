# CORE Quick Start Guide

CORE is a Flet app for selecting one object record from a CollectionBuilder metadata CSV, editing that single row, and saving the changes back to the file.

## Start Here

```bash
cd /Users/mcfatem/GitHub/CORE
./run.sh
```

On Windows, run `scripts\\run.bat` from the project folder.

## Typical Workflow

1. Open a project folder or browse directly to the metadata CSV file.
2. Choose one record from the dropdown.
3. Edit the generated form fields for that record.
4. Click Save Changes to write the row back to the CSV.

## What Gets Saved

CORE stores these local items in `~/CORE-data/`:

- the last project folder
- the last metadata CSV file
- the last selected record index
- application logs

## Helpful Files

- [README.md](README.md) - application overview
- [app.py](app.py) - runtime logic
- [run.sh](run.sh) - root shortcut launcher
- [scripts/run.sh](scripts/run.sh) - macOS/Linux launcher
- [scripts/run.bat](scripts/run.bat) - Windows launcher

## Validation

```bash
python3 -m py_compile app.py
```