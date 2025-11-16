# Universal Subtitle Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://doc.qt.io/qtforpython/)
[![CLI Support](https://img.shields.io/badge/Mode-Headless-orange.svg)](https://docs.python.org/3/library/argparse.html)

Universal Subtitle Converter is a robust, modular Python application designed to convert subtitle data (JSON, VTT) into standard formats like SRT, VTT, and plain text. 

Refactored with a "backend-agnostic" architecture, this tool separates the core conversion logic from the presentation layer, allowing you to use it as a **Headless CLI tool** for automation/servers or as a **Desktop Application** (PySide6/Tkinter).

## Features

- **Modular Architecture:** Core logic is completely decoupled from the UI, enabling easy integration into other pipelines.
- **Multi-Format Support:**
  - **Input:** JSON (YouTube/GDrive style), VTT.
  - **Output:** SRT, VTT, Plain Text (TXT), JSON.
- **Batch Processing:** Convert entire directories of subtitles at once.
- **Smart Naming:** Options to retain source names, add suffixes, or use custom filenames.
- **Dual Interfaces:**
  - **CLI:** Full-featured command-line interface for scripts and headless servers.
  - **GUI:** Modern PySide6 (Qt) interface or lightweight Tkinter interface.

## Getting Started

### Prerequisites

- Python 3.6+ installed on your system.

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/Universal-Subtitle-Converter.git](https://github.com/your-username/Universal-Subtitle-Converter.git)
   cd Universal-Subtitle-Converter
   ```

2. Create a virtual environment (Recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. Install the package in "editable" mode (installs dependencies and registers the CLI command):
   ```bash
   pip install -e .
   ```
   *Note: If you want to use the PySide6 GUI, ensure you install the optional requirements:*
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### 1. Headless (Command Line Interface)

Once installed, the tool registers the `subconvert` command globally in your environment.

**Basic Syntax:**
```bash
subconvert <input_path> -o <output_directory> [options]
```

**Examples:**

* **Convert a single file to SRT (default):**
    ```bash
    subconvert "video_subs.json" -o "./output"
    ```

* **Batch convert a directory to SRT and Plain Text:**
    ```bash
    subconvert "./raw_subs/" -o "./converted" --srt --txt
    ```

* **Convert VTT to SRT with a suffix:**
    ```bash
    subconvert "movie.vtt" -o "./final" --srt -f vtt -n source_with_suffix --suffix "_eng"
    ```

* **Organize outputs into separate subfolders:**
    ```bash
    subconvert "./subs/" -o "./dist" --srt --vtt --json -s
    ```

**CLI Help:**
Run `subconvert --help` to see all available flags and options.

### 2. Graphical User Interface (PySide6)

For a visual experience, launch the PySide6 application.

```bash
python -m src.subconverter.gui_pyside
```

**GUI Features:**
- **Input/Output Selection:** Drag-and-drop style file browsing.
- **Visual Progress:** Real-time progress bar for batch operations.
- **Format Toggles:** Checkboxes to easily select multiple output formats.
- **Naming Control:** Dropdown menus to select naming strategies without memorizing flags.

*(Note: A lightweight Tkinter version is also available via `python -m src.subconverter.gui_tkinter`)*

---

## Project Structure

The project follows the industry-standard `src` layout to ensure cleaner imports and distribution.

```
Universal-Subtitle-Converter/
├── src/
│   └── subconverter/
│       ├── __init__.py       # Package definition
│       ├── formats.py        # Core logic: Parsing and string formatting (Pure Python)
│       ├── processor.py      # Controller: File I/O, orchestration, and error handling
│       ├── cli.py            # Entry point: Argument parsing for headless mode
│       ├── gui_pyside.py     # Entry point: PySide6 (Qt) Window class
│       └── gui_tkinter.py    # Entry point: Tkinter Window class
├── setup.py                  # Installation script & CLI entry point registration
├── requirements.txt          # Dependencies (PySide6, etc.)
└── README.md                 # Documentation
```

## Contributing

Contributions are welcome! Because the logic is decoupled:
- **Logic improvements:** Edit `formats.py` or `processor.py`.
- **UI improvements:** Edit `gui_pyside.py` or `cli.py` without breaking the core logic.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
