import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QRadioButton, QComboBox,
    QCheckBox, QFileDialog, QMessageBox, QProgressBar
)
from . import processor  # Import our decoupled backend

class PySideConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Subtitle Converter")
        self.setGeometry(100, 100, 600, 620)

        # --- (All your UI creation code from _create_input_group, etc.) ---
        # --- (This code doesn't need to change) ---
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Input Section
        input_group = QWidget()
        layout = QGridLayout(input_group)
        self.mode_radio_single = QRadioButton("Single File"); self.mode_radio_single.setChecked(True)
        self.mode_radio_dir = QRadioButton("Directory (Batch)")
        layout.addWidget(self.mode_radio_single, 0, 0); layout.addWidget(self.mode_radio_dir, 0, 1)
        layout.addWidget(QLabel("Input Path:"), 1, 0)
        self.input_path_entry = QLineEdit()
        layout.addWidget(self.input_path_entry, 1, 1)
        self.browse_input_btn = QPushButton("Browse"); layout.addWidget(self.browse_input_btn, 1, 2)
        layout.addWidget(QLabel("Input Format:"), 2, 0)
        self.input_format_combo = QComboBox(); self.input_format_combo.addItems(["json", "vtt"])
        layout.addWidget(self.input_format_combo, 2, 1)
        main_layout.addWidget(input_group)

        # Output Section
        output_group = QWidget()
        layout = QGridLayout(output_group)
        layout.addWidget(QLabel("Output Directory:"), 0, 0)
        self.output_dir_entry = QLineEdit()
        layout.addWidget(self.output_dir_entry, 0, 1)
        self.browse_output_btn = QPushButton("Browse"); layout.addWidget(self.browse_output_btn, 0, 2)
        layout.addWidget(QLabel("Naming Strategy:"), 1, 0)
        self.naming_strategy_combo = QComboBox(); self.naming_strategy_combo.addItems(["source", "custom", "source_with_suffix"])
        layout.addWidget(self.naming_strategy_combo, 1, 1)
        layout.addWidget(QLabel("Custom Base Name:"), 2, 0)
        self.custom_name_entry = QLineEdit("output"); self.custom_name_entry.setEnabled(False)
        layout.addWidget(self.custom_name_entry, 2, 1)
        layout.addWidget(QLabel("Custom Suffix:"), 3, 0)
        self.suffix_entry = QLineEdit("_subtitle"); self.suffix_entry.setEnabled(False)
        layout.addWidget(self.suffix_entry, 3, 1)
        main_layout.addWidget(output_group)

        # Format options
        format_group = QWidget()
        layout = QGridLayout(format_group)
        self.export_srt_check = QCheckBox("SRT"); self.export_srt_check.setChecked(True)
        self.export_vtt_check = QCheckBox("VTT")
        self.export_txt_check = QCheckBox("Plain Text"); self.export_txt_check.setChecked(True)
        self.export_json_check = QCheckBox("JSON")
        layout.addWidget(self.export_srt_check, 0, 0); layout.addWidget(self.export_vtt_check, 0, 1)
        layout.addWidget(self.export_txt_check, 0, 2); layout.addWidget(self.export_json_check, 0, 3)
        self.separate_folders_check = QCheckBox("Use Separate Folders for Each Format")
        layout.addWidget(self.separate_folders_check, 1, 0, 1, 4)
        main_layout.addWidget(format_group)
        
        # Convert Button & Status
        self.convert_btn = QPushButton("Convert")
        main_layout.addWidget(self.convert_btn)
        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar(); self.progress_bar.setRange(0, 100)
        main_layout.addWidget(self.progress_bar)

        # Connect signals
        self.browse_input_btn.clicked.connect(self.browse_input)
        self.browse_output_btn.clicked.connect(self.browse_output_dir)
        self.naming_strategy_combo.currentIndexChanged.connect(self.toggle_custom_name)
        self.convert_btn.clicked.connect(self.convert)
        # -----------------------------------------------------------------

    # --- GUI helper methods (no change) ---
    def browse_input(self):
        input_format = self.input_format_combo.currentText()
        if self.mode_radio_single.isChecked():
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", f"{input_format.upper()} files (*.{input_format})")
            if file_path: self.input_path_entry.setText(file_path)
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
            if dir_path: self.input_path_entry.setText(dir_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path: self.output_dir_entry.setText(dir_path)

    def toggle_custom_name(self):
        strategy = self.naming_strategy_combo.currentText()
        self.custom_name_entry.setEnabled(strategy == "custom")
        self.suffix_entry.setEnabled(strategy == "source_with_suffix")

    # --- THIS IS THE KEY REFACTORED METHOD ---
    def convert(self):
        self.status_label.setText("Starting...")
        self.progress_bar.setValue(0)
        
        # 1. Build the config dictionary from the UI
        config = {
            "input_path": self.input_path_entry.text(),
            "output_dir": self.output_dir_entry.text(),
            "input_format": self.input_format_combo.currentText(),
            "is_directory": self.mode_radio_dir.isChecked(),
            
            "export_srt": self.export_srt_check.isChecked(),
            "export_vtt": self.export_vtt_check.isChecked(),
            "export_txt": self.export_txt_check.isChecked(),
            "export_json": self.export_json_check.isChecked(),
            
            "separate_folders": self.separate_folders_check.isChecked(),
            
            "naming_strategy": self.naming_strategy_combo.currentText(),
            "custom_name": self.custom_name_entry.text(),
            "suffix_text": self.suffix_entry.text(),
        }

        # 2. Validate input
        if not config["input_path"]:
            QMessageBox.warning(self, "Warning", "Please select an input file or directory!")
            return
        if not config["output_dir"]:
            QMessageBox.warning(self, "Warning", "Please select an output directory!")
            return
        if not any([config["export_srt"], config["export_txt"], config["export_vtt"], config["export_json"]]):
            QMessageBox.warning(self, "Warning", "Please select at least one output format!")
            return

        # 3. Define the progress callback for the GUI
        def gui_progress_callback(current, total, message):
            self.status_label.setText(message)
            if total > 0:
                self.progress_bar.setValue(int((current / total) * 100))
            QApplication.processEvents() # Update UI

        # 4. Run the conversion!
        try:
            processor.run_conversion(config, gui_progress_callback)
            QMessageBox.information(self, "Success", "Conversion completed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.status_label.setText(f"Error: {str(e)}")

# --- Main execution (no change) ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = PySideConverterApp()
    converter.show()
    sys.exit(app.exec())
