import json
import os
import re
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QComboBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)


class PySideConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subtitle Converter")
        self.setGeometry(100, 100, 600, 620)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Input Section
        input_group = self._create_input_group()
        main_layout.addWidget(input_group)

        # Output Section
        output_group = self._create_output_group()
        main_layout.addWidget(output_group)

        # Format options
        format_group = self._create_format_group()
        main_layout.addWidget(format_group)

        # Convert Button
        self.convert_btn = QPushButton("Convert")
        main_layout.addWidget(self.convert_btn)

        # Status
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)

        # Connect signals to slots
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        self.naming_strategy_combo.currentIndexChanged.connect(
            self.toggle_custom_name
        )
        self.convert_btn.clicked.connect(self.convert)

    def _create_input_group(self):
        input_group = QWidget()
        layout = QGridLayout(input_group)

        # Mode selection
        self.mode_radio_single = QRadioButton("Single File")
        self.mode_radio_single.setChecked(True)
        layout.addWidget(self.mode_radio_single, 0, 0)

        self.mode_radio_dir = QRadioButton("Directory (Batch)")
        layout.addWidget(self.mode_radio_dir, 0, 1)

        # Input Path
        layout.addWidget(QLabel("Input Path:"), 1, 0)
        self.input_path_entry = QLineEdit()
        layout.addWidget(self.input_path_entry, 1, 1)
        self.browse_input_btn = QPushButton("Browse")
        layout.addWidget(self.browse_input_btn, 1, 2)

        # Input Format
        layout.addWidget(QLabel("Input Format:"), 2, 0)
        self.input_format_combo = QComboBox()
        self.input_format_combo.addItems(["json", "vtt"])
        layout.addWidget(self.input_format_combo, 2, 1)

        return input_group

    def _create_output_group(self):
        output_group = QWidget()
        layout = QGridLayout(output_group)

        # Output Directory
        layout.addWidget(QLabel("Output Directory:"), 0, 0)
        self.output_dir_entry = QLineEdit()
        layout.addWidget(self.output_dir_entry, 0, 1)
        self.browse_output_btn = QPushButton("Browse")
        layout.addWidget(self.browse_output_btn, 0, 2)

        # Naming Strategy
        layout.addWidget(QLabel("Naming Strategy:"), 1, 0)
        self.naming_strategy_combo = QComboBox()
        self.naming_strategy_combo.addItems(
            ["source", "custom", "source_with_suffix"]
        )
        layout.addWidget(self.naming_strategy_combo, 1, 1)

        # Custom Base Name
        layout.addWidget(QLabel("Custom Base Name:"), 2, 0)
        self.custom_name_entry = QLineEdit("output")
        self.custom_name_entry.setEnabled(False)
        layout.addWidget(self.custom_name_entry, 2, 1)

        # Custom Suffix
        layout.addWidget(QLabel("Custom Suffix:"), 3, 0)
        self.suffix_entry = QLineEdit("_subtitle")
        self.suffix_entry.setEnabled(False)
        layout.addWidget(self.suffix_entry, 3, 1)

        return output_group

    def _create_format_group(self):
        format_group = QWidget()
        layout = QGridLayout(format_group)

        self.export_srt_check = QCheckBox("SRT")
        self.export_srt_check.setChecked(True)
        layout.addWidget(self.export_srt_check, 0, 0)

        self.export_vtt_check = QCheckBox("VTT")
        layout.addWidget(self.export_vtt_check, 0, 1)

        self.export_txt_check = QCheckBox("Plain Text")
        self.export_txt_check.setChecked(True)
        layout.addWidget(self.export_txt_check, 0, 2)

        self.export_json_check = QCheckBox("JSON")
        layout.addWidget(self.export_json_check, 0, 3)

        self.separate_folders_check = QCheckBox(
            "Use Separate Folders for Each Format"
        )
        layout.addWidget(self.separate_folders_check, 1, 0, 1, 4)

        return format_group

    def browse_input(self):
        input_format = self.input_format_combo.currentText()
        if self.mode_radio_single.isChecked():
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Input File", "", f"{input_format.upper()} files (*.{input_format})"
            )
            if file_path:
                self.input_path_entry.setText(file_path)
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
            if dir_path:
                self.input_path_entry.setText(dir_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_entry.setText(dir_path)

    def toggle_custom_name(self):
        strategy = self.naming_strategy_combo.currentText()
        if strategy == "custom":
            self.custom_name_entry.setEnabled(True)
            self.suffix_entry.setEnabled(False)
        elif strategy == "source_with_suffix":
            self.custom_name_entry.setEnabled(False)
            self.suffix_entry.setEnabled(True)
        else:  # source
            self.custom_name_entry.setEnabled(False)
            self.suffix_entry.setEnabled(False)

    def convert(self):
        input_path = self.input_path_entry.text()
        output_dir = self.output_dir_entry.text()
        input_format = self.input_format_combo.currentText()

        if not input_path:
            QMessageBox.warning(self, "Warning", "Please select an input file or directory!")
            return
        if not output_dir:
            QMessageBox.warning(self, "Warning", "Please select an output directory!")
            return
        if not any(
            [
                self.export_srt_check.isChecked(),
                self.export_txt_check.isChecked(),
                self.export_vtt_check.isChecked(),
                self.export_json_check.isChecked(),
            ]
        ):
            QMessageBox.warning(self, "Warning", "Please select at least one output format!")
            return

        # Create output directories if needed
        if self.separate_folders_check.isChecked():
            if self.export_srt_check.isChecked():
                os.makedirs(os.path.join(output_dir, "srt"), exist_ok=True)
            if self.export_vtt_check.isChecked():
                os.makedirs(os.path.join(output_dir, "vtt"), exist_ok=True)
            if self.export_txt_check.isChecked():
                os.makedirs(os.path.join(output_dir, "txt"), exist_ok=True)
            if self.export_json_check.isChecked():
                os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

        try:
            # Process single file
            if self.mode_radio_single.isChecked():
                expected_ext = ".json" if input_format == "json" else ".vtt"
                if not input_path.lower().endswith(expected_ext):
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"Selected file must be a {input_format.upper()} file!",
                    )
                    return

                self.process_single_file(input_path, output_dir, input_format)

            # Process directory (batch)
            else:
                extension = ".json" if input_format == "json" else ".vtt"
                target_files = [
                    f for f in os.listdir(input_path) if f.lower().endswith(extension)
                ]
                if not target_files:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"No {input_format.upper()} files found in the selected directory!",
                    )
                    return

                self.process_directory(
                    input_path, output_dir, target_files, input_format
                )

            self.status_label.setText("Conversion completed successfully!")
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", "Conversion completed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText(f"Error: {str(e)}")

    def process_single_file(self, input_file, output_dir, input_format):
        self.status_label.setText(f"Processing file: {os.path.basename(input_file)}...")
        self.progress_bar.setValue(0)
        QApplication.processEvents()

        # Get output filename
        output_base = self.get_output_filename(input_file)

        # Convert based on input format
        if input_format == "json":
            with open(input_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            subtitles = self.convert_json_to_subtitles(data)
        else:  # vtt
            with open(input_file, "r", encoding="utf-8") as f:
                vtt_content = f.read()
            subtitles = self.parse_vtt(vtt_content)

        self.progress_bar.setValue(50)
        QApplication.processEvents()

        self.save_output_files(subtitles, output_dir, output_base)
        self.progress_bar.setValue(100)

    def process_directory(self, input_dir, output_dir, target_files, input_format):
        total_files = len(target_files)
        self.status_label.setText(f"Processing {total_files} {input_format.upper()} files...")
        QApplication.processEvents()

        for i, filename in enumerate(target_files):
            try:
                input_file = os.path.join(input_dir, filename)
                self.status_label.setText(f"Processing file {i+1}/{total_files}: {filename}")
                self.progress_bar.setValue(int((i / total_files) * 100))
                QApplication.processEvents()

                # Get output filename
                output_base = self.get_output_filename(input_file)

                # Convert based on input format
                if input_format == "json":
                    with open(input_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    subtitles = self.convert_json_to_subtitles(data)
                else:  # vtt
                    with open(input_file, "r", encoding="utf-8") as f:
                        vtt_content = f.read()
                    subtitles = self.parse_vtt(vtt_content)

                self.save_output_files(subtitles, output_dir, output_base)

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Continue with next file

    def get_output_filename(self, input_file):
        """Determine the output filename based on the naming strategy"""
        strategy = self.naming_strategy_combo.currentText()
        filename = os.path.basename(input_file)
        base_name = os.path.splitext(filename)[0]

        if strategy == "source":
            return base_name
        elif strategy == "source_with_suffix":
            return f"{base_name}{self.suffix_entry.text()}"
        else:  # custom
            return self.custom_name_entry.text()

    def save_output_files(self, subtitles, output_dir, output_base):
        """Save the subtitle files in the selected formats"""
        # SRT format
        if self.export_srt_check.isChecked():
            srt_content = self.generate_srt(subtitles)
            if self.separate_folders_check.isChecked():
                srt_dir = os.path.join(output_dir, "srt")
                srt_path = os.path.join(srt_dir, f"{output_base}.srt")
            else:
                srt_path = os.path.join(output_dir, f"{output_base}.srt")

            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

        # VTT format
        if self.export_vtt_check.isChecked():
            vtt_content = self.generate_vtt(subtitles)
            if self.separate_folders_check.isChecked():
                vtt_dir = os.path.join(output_dir, "vtt")
                vtt_path = os.path.join(vtt_dir, f"{output_base}.vtt")
            else:
                vtt_path = os.path.join(output_dir, f"{output_base}.vtt")

            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write(vtt_content)

        # Plain text format
        if self.export_txt_check.isChecked():
            txt_content = self.generate_plain_text(subtitles)
            if self.separate_folders_check.isChecked():
                txt_dir = os.path.join(output_dir, "txt")
                txt_path = os.path.join(txt_dir, f"{output_base}.txt")
            else:
                txt_path = os.path.join(output_dir, f"{output_base}.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

        # JSON format
        if self.export_json_check.isChecked():
            json_data = self.generate_json(subtitles)
            if self.separate_folders_check.isChecked():
                json_dir = os.path.join(output_dir, "json")
                json_path = os.path.join(json_dir, f"{output_base}.json")
            else:
                json_path = os.path.join(output_dir, f"{output_base}.json")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

    # Conversion helper functions
    def ms_to_srt_time(self, ms):
        """Convert milliseconds to SRT format time (HH:MM:SS,MMM)"""
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

    def ms_to_vtt_time(self, ms):
        """Convert milliseconds to VTT format time (HH:MM:SS.MMM)"""
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{ms:03}"

    def time_to_ms(self, time_str):
        """Convert time string to milliseconds

        Handles both SRT format (HH:MM:SS,MMM) and VTT format (HH:MM:SS.MMM)
        """
        # Replace comma with dot to handle both SRT and VTT formats
        time_str = time_str.replace(",", ".")

        # Split hours, minutes, seconds, and milliseconds
        parts = time_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])

        # Split seconds and milliseconds
        sec_parts = parts[2].split(".")
        seconds = int(sec_parts[0])
        milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0

        # Convert to milliseconds
        return hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds

    def convert_json_to_subtitles(self, data):
        subtitles = []

        for event in data.get("events", []):
            if "segs" not in event or not event["segs"]:
                continue

            try:
                # Get timing information with fallback values
                start = event.get("tStartMs", 0)
                duration = event.get("dDurationMs", 0)
                end = start + duration

                # Extract text from segments
                text = "".join(seg.get("utf8", "") for seg in event["segs"])

                # Handle text appending
                if event.get("aAppend") == 1 and subtitles:
                    last_sub = subtitles[-1]
                    last_sub["text"] += text
                    last_sub["end"] = end
                else:
                    subtitles.append({"start": start, "end": end, "text": text})

            except KeyError as e:
                print(f"Skipping invalid event: Missing key {e}")
                continue

        return subtitles

    def parse_vtt(self, vtt_content):
        """Parse WebVTT format into a list of subtitle dictionaries"""
        subtitles = []

        # Remove WEBVTT header and split into cue blocks
        # First, normalize line endings
        vtt_content = vtt_content.replace("\r\n", "\n")

        # Skip the WEBVTT header
        if vtt_content.strip().startswith("WEBVTT"):
            vtt_content = re.sub(r"^WEBVTT.*?\n\n", "", vtt_content, flags=re.DOTALL)

        # Split content by double newlines to get cue blocks
        cue_blocks = re.split(r"\n\n+", vtt_content.strip())

        for block in cue_blocks:
            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue  # Skip incomplete blocks

            # The first line that contains "-->" is the timing line
            timing_line_idx = next(
                (i for i, line in enumerate(lines) if "-->" in line), -1
            )
            if timing_line_idx == -1:
                continue  # Skip blocks without timing information

            # Extract timing info
            timing_match = re.search(
                r"(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)", lines[timing_line_idx]
            )
            if not timing_match:
                continue

            start_time, end_time = timing_match.groups()

            # Convert times to milliseconds
            start_ms = self.time_to_ms(start_time)
            end_ms = self.time_to_ms(end_time)

            # Get all text lines after the timing line
            text = "\n".join(lines[timing_line_idx + 1 :])

            subtitles.append({"start": start_ms, "end": end_ms, "text": text})

        return subtitles

    def generate_srt(self, subtitles):
        """Generate SRT format subtitle content"""
        srt = []
        for i, sub in enumerate(subtitles, 1):
            start = self.ms_to_srt_time(sub["start"])
            end = self.ms_to_srt_time(sub["end"])
            srt.append(f"{i}\n{start} --> {end}\n{sub['text'].strip()}\n")
        return "\n".join(srt)

    def generate_vtt(self, subtitles):
        """Generate WebVTT format subtitle content"""
        vtt = ["WEBVTT\n"]  # WebVTT header

        for i, sub in enumerate(subtitles, 1):
            start = self.ms_to_vtt_time(sub["start"])
            end = self.ms_to_vtt_time(sub["end"])
            # In VTT, cue identifier is optional but useful for debugging
            vtt.append(f"\n{i}\n{start} --> {end}\n{sub['text'].strip()}")

        return "\n".join(vtt)

    def generate_plain_text(self, subtitles):
        """Generate plain text from subtitles (just the text content)"""
        return " ".join(sub["text"].strip() for sub in subtitles)

    def generate_json(self, subtitles):
        """Generate JSON format from subtitles (simplified structure)"""
        events = []

        for sub in subtitles:
            event = {
                "tStartMs": sub["start"],
                "dDurationMs": sub["end"] - sub["start"],
                "segs": [{"utf8": sub["text"]}],
            }
            events.append(event)

        return {"events": events}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = PySideConverterApp()
    converter.show()
    sys.exit(app.exec())
