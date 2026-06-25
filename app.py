"""CORE - Collection Object Record Editor.

A Flet desktop application for selecting a single row from a project's
CollectionBuilder metadata CSV file, inspecting its structure and content,
editing the row in a generated form, and saving changes back to the CSV.
"""

import csv
import json
import logging
import os
import platform
import socket
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import flet as ft


def get_app_version() -> str:
    """Read app version from the repository VERSION file."""
    try:
        version_file = Path(__file__).parent / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8").strip()
    except Exception:
        # Keep startup resilient if version metadata is unavailable.
        pass
    return "unknown"


APP_VERSION = get_app_version()


# Configure logging
DATA_DIR = Path.home() / "CORE-data"
os.makedirs(DATA_DIR / "logfiles", exist_ok=True)
log_filename = DATA_DIR / "logfiles" / f"core_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler, console_handler])
logger = logging.getLogger(__name__)

logging.getLogger("flet").setLevel(logging.WARNING)
logging.getLogger("flet_core").setLevel(logging.WARNING)
logging.getLogger("flet_desktop").setLevel(logging.WARNING)


PERSISTENCE_FILE = DATA_DIR / "persistent.json"
DEFAULT_UI_STATE = {
    "last_project_dir": "",
    "last_metadata_csv": "",
    "last_record_index": 0,
}

PREFERRED_LABEL_FIELDS = (
    "identifier",
    "object_id",
    "objectid",
    "local_identifier",
    "item_id",
    "call_number",
    "title",
    "name",
    "filename",
    "file_name",
)

MULTILINE_HINTS = (
    "description",
    "abstract",
    "note",
    "notes",
    "summary",
    "transcript",
    "caption",
    "subject",
    "content",
    "keywords",
    "text",
)


class PersistentStorage:
    """Handle persistent storage of UI state."""

    def __init__(self):
        self.data = self.load()

    def load(self) -> dict:
        """Load persistent data from disk."""
        try:
            if os.path.exists(PERSISTENCE_FILE):
                with open(PERSISTENCE_FILE, "r", encoding="utf-8") as file_handle:
                    data = json.load(file_handle)
                logger.info(f"Loaded persistent data from {PERSISTENCE_FILE}")
                return data
        except Exception as error:
            logger.warning(f"Could not load persistent data: {error}")

        return {"ui_state": dict(DEFAULT_UI_STATE)}

    def save(self):
        """Save persistent data to disk."""
        try:
            with open(PERSISTENCE_FILE, "w", encoding="utf-8") as file_handle:
                json.dump(self.data, file_handle, indent=2, ensure_ascii=False)
            logger.debug(f"Saved persistent data to {PERSISTENCE_FILE}")
        except Exception as error:
            logger.error(f"Could not save persistent data: {error}")

    def set_ui_state(self, field: str, value):
        """Update a UI state field."""
        self.data.setdefault("ui_state", dict(DEFAULT_UI_STATE))
        self.data["ui_state"][field] = value
        self.save()

    def get_ui_state(self, field: str, default=""):
        """Read a UI state field."""
        self.data.setdefault("ui_state", dict(DEFAULT_UI_STATE))
        return self.data["ui_state"].get(field, default)


def safe_text(value) -> str:
    """Return a safe string representation for CSV values."""
    if value is None:
        return ""
    return str(value)


def truncate_text(value: str, length: int = 60) -> str:
    """Trim long text for compact labels."""
    if len(value) <= length:
        return value
    return value[: length - 1].rstrip() + "…"


def build_record_label(row: dict, headers: List[str], index: int) -> str:
    """Create a human-friendly label for a record dropdown option."""
    lowered_headers = {header.lower(): header for header in headers}

    for preferred in PREFERRED_LABEL_FIELDS:
        header = lowered_headers.get(preferred)
        if header:
            candidate = safe_text(row.get(header, "")).strip()
            if candidate:
                return f"{index + 1}. {header}: {truncate_text(candidate)}"

    for header in headers:
        candidate = safe_text(row.get(header, "")).strip()
        if candidate:
            return f"{index + 1}. {header}: {truncate_text(candidate)}"

    return f"{index + 1}. Record"


def summarize_row(row: dict, headers: List[str], limit: int = 4) -> str:
    """Summarize a record using the first few populated fields."""
    parts = []
    for header in headers:
        value = safe_text(row.get(header, "")).strip()
        if value:
            parts.append(f"{header}={truncate_text(value, 36)}")
        if len(parts) >= limit:
            break
    return "; ".join(parts) if parts else "No populated values"


def discover_metadata_csv(project_dir: Path) -> Optional[Path]:
    """Find a likely metadata CSV file inside a project folder."""
    if project_dir.is_file() and project_dir.suffix.lower() == ".csv":
        return project_dir

    if not project_dir.exists() or not project_dir.is_dir():
        return None

    patterns = (
        "*metadata*.csv",
        "*collectionbuilder*.csv",
        "*collection*.csv",
        "*.csv",
    )

    for pattern in patterns:
        matches = sorted(project_dir.glob(pattern))
        if matches:
            return matches[0]

    return None


def load_metadata_csv(csv_path: Path) -> Tuple[List[str], List[dict], str]:
    """Load headers and rows from a metadata CSV file."""
    try:
        if not csv_path.exists():
            return [], [], f"Metadata CSV not found: {csv_path}"

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as file_handle:
            reader = csv.DictReader(file_handle)
            headers = list(reader.fieldnames or [])
            if not headers:
                return [], [], f"No headers found in {csv_path.name}"

            rows: List[dict] = []
            for raw_row in reader:
                normalized_row = {header: safe_text(raw_row.get(header, "")) for header in headers}
                if any(value.strip() for value in normalized_row.values()):
                    rows.append(normalized_row)

        return headers, rows, ""
    except Exception as error:
        logger.error(f"Could not load metadata CSV {csv_path}: {error}")
        return [], [], f"Error loading metadata CSV: {error}"


def save_metadata_csv(csv_path: Path, headers: List[str], rows: List[dict]) -> Tuple[bool, str]:
    """Write the edited rows back to the metadata CSV file."""
    try:
        with open(csv_path, "w", encoding="utf-8", newline="") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=headers, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({header: safe_text(row.get(header, "")) for header in headers})
        return True, str(csv_path)
    except Exception as error:
        logger.error(f"Could not save metadata CSV {csv_path}: {error}")
        return False, f"Error saving metadata CSV: {error}"


def is_multiline_field(header: str, value: str) -> bool:
    """Decide whether a field should render as multiline."""
    lowered = header.lower()
    if "\n" in value:
        return True
    if len(value) > 120:
        return True
    return any(hint in lowered for hint in MULTILINE_HINTS)


def main(page: ft.Page):
    page.title = f"CORE v{APP_VERSION} - Collection Object Record Editor"
    page.padding = 16
    page.window.width = 1280
    page.window.height = 980
    page.window.min_width = 1100
    page.window.min_height = 760
    page.scroll = ft.ScrollMode.AUTO
    page.bgcolor = ft.Colors.BLUE_GREY_50

    storage = PersistentStorage()
    logger.info("CORE application started")

    current_project_dir: Optional[Path] = None
    current_csv_path: Optional[Path] = None
    csv_headers: List[str] = []
    csv_rows: List[dict] = []
    selected_record_index = int(storage.get_ui_state("last_record_index", 0) or 0)
    form_fields: dict = {}

    stored_project_dir = safe_text(storage.get_ui_state("last_project_dir", "")).strip()
    if stored_project_dir and Path(stored_project_dir).exists():
        current_project_dir = Path(stored_project_dir)

    stored_csv_path = safe_text(storage.get_ui_state("last_metadata_csv", "")).strip()
    if stored_csv_path and Path(stored_csv_path).exists():
        current_csv_path = Path(stored_csv_path)

    project_dir_field = None
    metadata_csv_field = None
    record_dropdown = None
    overview_text = None
    structure_text = None
    selection_text = None
    preview_text = None
    record_form_column = None
    status_text = None
    log_output = None

    def add_log_message(text: str):
        """Prepend a timestamped message to the log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        existing = log_output.value or ""
        log_output.value = f"[{timestamp}] {text}\n{existing}"
        page.update()

    def update_status(message: str, is_error: bool = False):
        """Update the status line and mirror the message in the log."""
        status_text.value = message
        status_text.color = ft.Colors.RED_700 if is_error else ft.Colors.BLUE_GREY_900
        add_log_message(message)

    def refresh_selector():
        """Refresh the record dropdown using the current rows."""
        nonlocal selected_record_index

        if record_dropdown is None:
            return

        record_dropdown.options = [
            ft.dropdown.Option(key=str(index), text=build_record_label(row, csv_headers, index))
            for index, row in enumerate(csv_rows)
        ]

        if csv_rows:
            if selected_record_index < 0 or selected_record_index >= len(csv_rows):
                selected_record_index = 0
            record_dropdown.value = str(selected_record_index)
            record_dropdown.disabled = False
        else:
            selected_record_index = -1
            record_dropdown.value = None
            record_dropdown.disabled = True

        storage.set_ui_state("last_record_index", selected_record_index if selected_record_index >= 0 else 0)

    def update_overview():
        """Update the visible summary of the selected metadata row."""
        if not csv_headers:
            overview_text.value = "Load a project folder or a metadata CSV file to start editing."
            structure_text.value = "CORE builds a single-record form from the selected row of CollectionBuilder metadata."
            selection_text.value = ""
            preview_text.value = ""
            return

        overview_text.value = f"{len(csv_rows)} record(s) loaded across {len(csv_headers)} field(s)."
        structure_text.value = "Detected columns: " + ", ".join(csv_headers[:10]) + (
            " ..." if len(csv_headers) > 10 else ""
        )

        if 0 <= selected_record_index < len(csv_rows):
            selected_row = csv_rows[selected_record_index]
            selection_text.value = (
                f"Selected record {selected_record_index + 1} of {len(csv_rows)}: "
                f"{build_record_label(selected_row, csv_headers, selected_record_index)}"
            )
            preview_text.value = "Selected row preview: " + summarize_row(selected_row, csv_headers)
        else:
            selection_text.value = f"No record selected. {len(csv_rows)} record(s) available."
            preview_text.value = ""

    def render_record_form():
        """Build the edit form for the current record."""
        nonlocal form_fields
        form_fields = {}

        controls = []

        if not csv_headers:
            controls.append(
                ft.Text(
                    "Select a metadata CSV file to generate a single-record form.",
                    selectable=True,
                    color=ft.Colors.BLUE_GREY_700,
                )
            )
            record_form_column.controls = controls
            page.update()
            return

        if csv_rows and 0 <= selected_record_index < len(csv_rows):
            source_row = csv_rows[selected_record_index]
        else:
            source_row = {header: "" for header in csv_headers}

        for header in csv_headers:
            value = safe_text(source_row.get(header, ""))
            multiline = is_multiline_field(header, value)
            field = ft.TextField(
                label=header,
                value=value,
                multiline=multiline,
                min_lines=3 if multiline else 1,
                max_lines=10 if multiline else 1,
                expand=True,
            )
            form_fields[header] = field
            controls.append(field)

        if not csv_rows:
            controls.insert(
                0,
                ft.Text(
                    "This metadata CSV currently has no data rows. Use New Record to add one.",
                    selectable=True,
                    color=ft.Colors.BLUE_GREY_700,
                ),
            )

        record_form_column.controls = controls
        page.update()

    def load_metadata_into_editor(csv_path: Path, context_label: str = "Metadata CSV"):
        """Load a CSV file into the editor and refresh the form."""
        nonlocal current_project_dir, current_csv_path, csv_headers, csv_rows, selected_record_index

        headers, rows, error = load_metadata_csv(csv_path)
        if error:
            update_status(error, is_error=True)
            return

        csv_headers = headers
        csv_rows = rows
        current_csv_path = csv_path
        current_project_dir = csv_path.parent

        selected_record_index = int(storage.get_ui_state("last_record_index", 0) or 0)
        if csv_rows:
            if selected_record_index < 0 or selected_record_index >= len(csv_rows):
                selected_record_index = 0
        else:
            selected_record_index = -1

        project_dir_field.value = str(current_project_dir)
        metadata_csv_field.value = str(current_csv_path)

        storage.set_ui_state("last_project_dir", str(current_project_dir))
        storage.set_ui_state("last_metadata_csv", str(current_csv_path))
        storage.set_ui_state("last_record_index", selected_record_index if selected_record_index >= 0 else 0)

        refresh_selector()
        update_overview()
        render_record_form()

        if csv_rows:
            update_status(
                f"Loaded {len(csv_rows)} record(s) from {current_csv_path.name} for editing."
            )
        else:
            update_status(f"Loaded {current_csv_path.name}; no editable rows were found yet.")

        logger.info(
            f"{context_label}: loaded {len(csv_rows)} record(s) and {len(csv_headers)} field(s) from {current_csv_path}"
        )

    def load_project_folder(project_dir: Path):
        """Load the most likely metadata CSV from a project folder."""
        nonlocal current_project_dir, current_csv_path, csv_headers, csv_rows, selected_record_index

        current_project_dir = project_dir
        project_dir_field.value = str(project_dir)
        storage.set_ui_state("last_project_dir", str(project_dir))

        csv_path = discover_metadata_csv(project_dir)
        if csv_path:
            metadata_csv_field.value = str(csv_path)
            storage.set_ui_state("last_metadata_csv", str(csv_path))
            load_metadata_into_editor(csv_path, "Project folder")
        else:
            current_csv_path = None
            csv_headers = []
            csv_rows = []
            selected_record_index = -1
            refresh_selector()
            update_overview()
            render_record_form()
            update_status(
                f"No CSV file was found in {project_dir.name}. Choose a metadata CSV directly.",
                is_error=True,
            )

    def on_project_dir_result(event: ft.FilePickerResultEvent):
        if event.path:
            load_project_folder(Path(event.path))

    def on_csv_file_result(event: ft.FilePickerResultEvent):
        if event.files and event.files[0].path:
            load_metadata_into_editor(Path(event.files[0].path), "CSV file picker")

    def on_record_change(event):
        nonlocal selected_record_index

        if event.control.value is None:
            return

        try:
            selected_record_index = int(event.control.value)
        except (TypeError, ValueError):
            return

        storage.set_ui_state("last_record_index", selected_record_index)
        render_record_form()
        update_overview()
        if 0 <= selected_record_index < len(csv_rows):
            update_status(f"Selected {build_record_label(csv_rows[selected_record_index], csv_headers, selected_record_index)}")

    def on_reload_click(event):
        if current_csv_path and current_csv_path.exists():
            load_metadata_into_editor(current_csv_path, "Reload")
        else:
            update_status("Select a metadata CSV file before reloading.", is_error=True)

    def on_new_record_click(event):
        nonlocal selected_record_index

        if not csv_headers:
            update_status("Load a metadata CSV file before adding a record.", is_error=True)
            return

        csv_rows.append({header: "" for header in csv_headers})
        selected_record_index = len(csv_rows) - 1
        storage.set_ui_state("last_record_index", selected_record_index)
        refresh_selector()
        render_record_form()
        update_overview()
        update_status(f"Added a new blank record at position {selected_record_index + 1}.")

    def on_save_click(event):
        nonlocal selected_record_index

        if not current_csv_path:
            update_status("Select a metadata CSV file before saving.", is_error=True)
            return

        if not csv_headers:
            update_status("No metadata headers are available to save.", is_error=True)
            return

        if selected_record_index < 0 or selected_record_index >= len(csv_rows):
            csv_rows.append({header: "" for header in csv_headers})
            selected_record_index = len(csv_rows) - 1

        target_row = csv_rows[selected_record_index]
        for header, field in form_fields.items():
            target_row[header] = safe_text(field.value)

        ok, result = save_metadata_csv(current_csv_path, csv_headers, csv_rows)
        if not ok:
            update_status(result, is_error=True)
            return

        storage.set_ui_state("last_record_index", selected_record_index)
        refresh_selector()
        update_overview()
        update_status(f"Saved record {selected_record_index + 1} to {current_csv_path.name}.")
        logger.info(f"Saved metadata CSV to {result}")

    def on_copy_status_click(event):
        if status_text.value:
            page.set_clipboard(status_text.value)
            add_log_message("Status copied to clipboard")

    def on_copy_log_click(event):
        if log_output.value:
            page.set_clipboard(log_output.value)
            add_log_message("Log output copied to clipboard")

    def on_clear_log_click(event):
        log_output.value = ""
        page.update()
        logger.info("Log cleared")

    project_picker = ft.FilePicker(on_result=on_project_dir_result)
    csv_picker = ft.FilePicker(on_result=on_csv_file_result)
    page.overlay.extend([project_picker, csv_picker])

    project_dir_field = ft.TextField(
        label="Project Folder",
        value=str(current_project_dir) if current_project_dir else "",
        read_only=True,
        expand=True,
    )

    metadata_csv_field = ft.TextField(
        label="Metadata CSV File",
        value=str(current_csv_path) if current_csv_path else "",
        read_only=True,
        expand=True,
    )

    record_dropdown = ft.Dropdown(
        label="Single Record",
        hint_text="Choose one object record",
        width=700,
        options=[],
        on_change=on_record_change,
    )

    overview_text = ft.Text(
        "Load a project folder or metadata CSV file to begin.",
        size=14,
        weight=ft.FontWeight.BOLD,
        selectable=True,
    )

    structure_text = ft.Text(
        "CORE will infer the row structure from the metadata CSV headers.",
        size=12,
        color=ft.Colors.BLUE_GREY_700,
        selectable=True,
    )

    selection_text = ft.Text(
        "",
        size=12,
        color=ft.Colors.BLUE_GREY_700,
        selectable=True,
    )

    preview_text = ft.Text(
        "",
        size=12,
        color=ft.Colors.BLUE_GREY_700,
        selectable=True,
    )

    record_form_column = ft.Column(
        controls=[],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    status_text = ft.TextField(
        value="Ready",
        multiline=True,
        min_lines=2,
        max_lines=3,
        read_only=True,
    )

    log_output = ft.TextField(
        value="",
        multiline=True,
        min_lines=8,
        max_lines=8,
        read_only=True,
    )

    header_card = ft.Container(
        bgcolor=ft.Colors.BLUE_900,
        border_radius=18,
        padding=24,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FORMAT_LIST_BULLETED, size=30, color=ft.Colors.WHITE),
                        ft.Text(
                            f"CORE v{APP_VERSION}",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text(
                    "Collection Object Record Editor",
                    size=16,
                    color=ft.Colors.BLUE_100,
                    weight=ft.FontWeight.W_500,
                ),
                ft.Text(
                    "Select one object record from a CollectionBuilder metadata CSV, edit it in place, and save the row back to the same file.",
                    size=13,
                    color=ft.Colors.WHITE,
                ),
            ],
            spacing=8,
        ),
    )

    source_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=18,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        content=ft.Column(
            controls=[
                ft.Text("Project Source", size=18, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[
                        project_dir_field,
                        ft.ElevatedButton(
                            "Browse Folder",
                            icon=ft.Icons.FOLDER_OPEN,
                            on_click=lambda _: project_picker.get_directory_path(
                                dialog_title="Select Project Folder"
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    controls=[
                        metadata_csv_field,
                        ft.ElevatedButton(
                            "Browse CSV",
                            icon=ft.Icons.FILE_OPEN,
                            on_click=lambda _: csv_picker.pick_files(
                                dialog_title="Select Metadata CSV",
                                allow_multiple=False,
                            ),
                        ),
                    ],
                ),
            ],
            spacing=10,
        ),
    )

    selector_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=18,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Record Selection", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    "Choose a single object record to inspect or edit.",
                                    size=12,
                                    color=ft.Colors.BLUE_GREY_700,
                                    italic=True,
                                ),
                                record_dropdown,
                            ],
                            spacing=6,
                            expand=True,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Actions", size=18, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    controls=[
                                        ft.ElevatedButton(
                                            "Reload",
                                            icon=ft.Icons.REFRESH,
                                            on_click=on_reload_click,
                                        ),
                                        ft.ElevatedButton(
                                            "New Record",
                                            icon=ft.Icons.ADD,
                                            on_click=on_new_record_click,
                                        ),
                                        ft.ElevatedButton(
                                            "Save Changes",
                                            icon=ft.Icons.SAVE,
                                            on_click=on_save_click,
                                        ),
                                    ],
                                    wrap=True,
                                ),
                            ],
                            spacing=6,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
        ),
    )

    editor_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=18,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        content=ft.Column(
            controls=[
                ft.Text("Record Details", size=18, weight=ft.FontWeight.BOLD),
                overview_text,
                structure_text,
                selection_text,
                preview_text,
                ft.Container(height=4),
                ft.Container(
                    border_radius=12,
                    padding=14,
                    bgcolor=ft.Colors.BLUE_GREY_50,
                    content=record_form_column,
                    height=520,
                ),
            ],
            spacing=8,
        ),
    )

    status_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=18,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Status", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CONTENT_COPY,
                            tooltip="Copy status to clipboard",
                            on_click=on_copy_status_click,
                            icon_size=20,
                        ),
                    ],
                ),
                status_text,
            ],
            spacing=8,
        ),
    )

    log_card = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        padding=18,
        border=ft.border.all(1, ft.Colors.BLUE_GREY_100),
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Activity Log", size=18, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_SWEEP,
                            tooltip="Clear log",
                            on_click=on_clear_log_click,
                            icon_size=20,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CONTENT_COPY,
                            tooltip="Copy log to clipboard",
                            on_click=on_copy_log_click,
                            icon_size=20,
                        ),
                    ],
                ),
                log_output,
            ],
            spacing=8,
        ),
    )

    page.add(
        ft.Column(
            controls=[
                header_card,
                source_card,
                selector_card,
                editor_card,
                status_card,
                log_card,
            ],
            spacing=16,
        )
    )

    if current_csv_path and current_csv_path.exists():
        load_metadata_into_editor(current_csv_path, "Session restore")
    elif current_project_dir and current_project_dir.exists():
        load_project_folder(current_project_dir)
    else:
        refresh_selector()
        update_overview()
        render_record_form()
        update_status(f"CORE v{APP_VERSION} ready. Open a project folder or metadata CSV file to begin.")

    page.update()
    logger.info(
        f"UI initialised successfully on {socket.gethostname()} running {platform.system()} {platform.release()}"
    )


if __name__ == "__main__":
    logger.info("Application starting…")
    ft.app(target=main)