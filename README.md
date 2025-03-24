---
### GitHub Repository Title

**Universal Subtitle Converter (JSON ➜ SRT/TXT for GDrive, YouTube & More)**

---

### README.md

````markdown
# Universal Subtitle Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green.svg)](https://docs.python.org/3/library/tkinter.html)

Universal Subtitle Converter is a user-friendly desktop application that converts subtitle data stored in JSON format into SRT and plain text (TXT) files. Designed to work with subtitle files generated from various sources including Google Drive videos and YouTube, this tool makes it simple to create standard subtitle formats for media projects.

## Features

- **Multi-Source Support:** Works with JSON subtitle files generated from GDrive videos, YouTube, and more.
- **Dual Output Formats:** Converts JSON subtitles to both SRT (for video players) and plain text files.
- **Intuitive GUI:** Built with Tkinter for a straightforward, user-friendly experience.
- **Error Handling:** Alerts for missing inputs and conversion errors.

## Getting Started

### Prerequisites

- Python 3.x installed on your system.
- Tkinter (usually comes pre-installed with Python).

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/Universal-Subtitle-Converter.git
   ```
````

2. Navigate into the project directory:
   ```bash
   cd Universal-Subtitle-Converter
   ```
3. (Optional) Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
4. Install any necessary dependencies (if additional dependencies are added in the future):
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Run the application:
   ```bash
   python subtitle_converter.py
   ```
2. In the GUI:
   - Click **Browse** to select your input JSON file containing subtitle data.
   - Select an output directory where you want the SRT and TXT files to be saved.
   - Specify a base name for the output files.
   - Click **Convert** to generate the subtitle files.
3. Upon successful conversion, a message box will display the paths to your newly created files.

## Documentation

### How It Works

- **Input:** The tool accepts a JSON file containing subtitle events with timing information.
- **Processing:** It extracts subtitle segments, merges overlapping segments if needed, and formats them according to SRT specifications.
- **Output:** The application produces two files:
  - A `.srt` file for use with most media players.
  - A `.txt` file for plain text transcript usage.

### Code Structure

- **`subtitle_converter.py`:** Main application file containing the Tkinter GUI and conversion logic.
- **Functions:**
  - `browse_input()` & `browse_output_dir()`: Handle file and directory selection.
  - `convert()`: Validates inputs, processes the JSON data, and writes output files.
  - `ms_to_srt_time()`, `convert_json_to_subtitles()`, `generate_srt()`, `generate_plain_text()`: Functions to handle time conversion and subtitle generation.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Icons & Badges

The repository includes several badges and icons to quickly communicate project information:

- **License Badge:** Displays the MIT license.
- **Python Version Badge:** Indicates compatibility with Python 3.x.
- **GUI Badge:** Highlights the use of Tkinter for the user interface.

---

Enjoy using the Universal Subtitle Converter! If you have any questions or run into issues, please open an issue on GitHub.

```

```
