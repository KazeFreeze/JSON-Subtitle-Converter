import json
import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, IntVar, StringVar


class SubtitleConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Converter")
        self.root.geometry("600x620")  # Increased height to accommodate new options

        # Create main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text="Input")
        input_frame.pack(fill=tk.X, pady=5)

        # Mode selection (single file vs directory)
        self.mode = IntVar(value=0)  # 0: single file, 1: directory
        ttk.Radiobutton(
            input_frame,
            text="Single File",
            variable=self.mode,
            value=0,
            command=self.toggle_input_mode,
        ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(
            input_frame,
            text="Directory (Batch)",
            variable=self.mode,
            value=1,
            command=self.toggle_input_mode,
        ).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Input File/Directory Selection
        ttk.Label(input_frame, text="Input Path:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.input_path = StringVar()
        self.input_entry = ttk.Entry(
            input_frame, textvariable=self.input_path, width=40
        )
        self.input_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")
        self.browse_input_btn = ttk.Button(
            input_frame, text="Browse", command=self.browse_input
        )
        self.browse_input_btn.grid(row=1, column=2, padx=5, pady=5)

        # Input Format Selection
        ttk.Label(input_frame, text="Input Format:").grid(
            row=2, column=0, padx=5, pady=5, sticky="w"
        )
        self.input_format = StringVar(value="json")
        input_format_combobox = ttk.Combobox(
            input_frame,
            textvariable=self.input_format,
            values=["json", "vtt"],
            width=15,
            state="readonly",
        )
        input_format_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        input_format_combobox.bind(
            "<<ComboboxSelected>>", self.update_file_browser_filter
        )

        # Output Section
        output_frame = ttk.LabelFrame(main_frame, text="Output")
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="Output Directory:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.output_dir = StringVar()
        ttk.Entry(output_frame, textvariable=self.output_dir, width=40).grid(
            row=0, column=1, padx=5, pady=5, sticky="we"
        )
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Naming options
        ttk.Label(output_frame, text="Naming Strategy:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.naming_strategy = StringVar(value="source")
        naming_combobox = ttk.Combobox(
            output_frame,
            textvariable=self.naming_strategy,
            values=["source", "custom", "source_with_suffix"],
            width=15,
            state="readonly",
        )
        naming_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        naming_combobox.bind("<<ComboboxSelected>>", self.toggle_custom_name)

        # Custom base name
        ttk.Label(output_frame, text="Custom Base Name:").grid(
            row=2, column=0, padx=5, pady=5, sticky="w"
        )
        self.output_name = StringVar(value="output")
        self.custom_name_entry = ttk.Entry(
            output_frame, textvariable=self.output_name, width=40
        )
        self.custom_name_entry.grid(row=2, column=1, padx=5, pady=5, sticky="we")
        self.custom_name_entry.configure(
            state="disabled"
        )  # Initially disabled as source is selected

        # Custom suffix (for source_with_suffix option)
        ttk.Label(output_frame, text="Custom Suffix:").grid(
            row=3, column=0, padx=5, pady=5, sticky="w"
        )
        self.suffix = StringVar(value="_subtitle")
        self.suffix_entry = ttk.Entry(output_frame, textvariable=self.suffix, width=40)
        self.suffix_entry.grid(row=3, column=1, padx=5, pady=5, sticky="we")
        self.suffix_entry.configure(state="disabled")  # Initially disabled

        # Format options
        format_frame = ttk.LabelFrame(main_frame, text="Output Formats")
        format_frame.pack(fill=tk.X, pady=5)

        self.export_srt = IntVar(value=1)
        ttk.Checkbutton(format_frame, text="SRT", variable=self.export_srt).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.export_vtt = IntVar(value=0)
        ttk.Checkbutton(format_frame, text="VTT", variable=self.export_vtt).grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )

        self.export_txt = IntVar(value=1)
        ttk.Checkbutton(format_frame, text="Plain Text", variable=self.export_txt).grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )

        self.export_json = IntVar(value=0)  # Added JSON output option
        ttk.Checkbutton(format_frame, text="JSON", variable=self.export_json).grid(
            row=0, column=3, padx=5, pady=5, sticky="w"
        )

        self.separate_folders = IntVar(value=0)
        ttk.Checkbutton(
            format_frame,
            text="Use Separate Folders for Each Format",
            variable=self.separate_folders,
        ).grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")

        # Convert Button
        convert_frame = ttk.Frame(main_frame)
        convert_frame.pack(fill=tk.X, pady=10)
        ttk.Button(convert_frame, text="Convert", command=self.convert).pack(pady=5)

        # Status
        self.status_var = StringVar()
        self.status = ttk.Label(
            main_frame, textvariable=self.status_var, foreground="blue", wraplength=580
        )
        self.status.pack(fill=tk.X, pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, orient="horizontal", length=580, mode="determinate"
        )
        self.progress.pack(fill=tk.X, pady=5)
        self.progress["maximum"] = 100
        self.progress["value"] = 0

    def update_file_browser_filter(self, event=None):
        """Update the file browser filter based on selected input format"""
        # Reset the input path when format changes
        self.input_path.set("")

    def toggle_input_mode(self):
        self.browse_input()  # Reset the input path

    def toggle_custom_name(self, event=None):
        strategy = self.naming_strategy.get()
        if strategy == "custom":
            self.custom_name_entry.configure(state="normal")
            self.suffix_entry.configure(state="disabled")
        elif strategy == "source_with_suffix":
            self.custom_name_entry.configure(state="disabled")
            self.suffix_entry.configure(state="normal")
        else:  # source
            self.custom_name_entry.configure(state="disabled")
            self.suffix_entry.configure(state="disabled")

    def browse_input(self):
        input_format = self.input_format.get()
        filetypes = (
            [("JSON files", "*.json")]
            if input_format == "json"
            else [("VTT files", "*.vtt")]
        )

        if self.mode.get() == 0:  # Single file
            file_path = filedialog.askopenfilename(filetypes=filetypes)
            if file_path:
                self.input_path.set(file_path)
        else:  # Directory
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.input_path.set(dir_path)

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)

    def convert(self):
        input_path = self.input_path.get()
        output_dir = self.output_dir.get()
        input_format = self.input_format.get()

        if not input_path:
            messagebox.showwarning(
                "Warning", "Please select an input file or directory!"
            )
            return
        if not output_dir:
            messagebox.showwarning("Warning", "Please select an output directory!")
            return
        if not any(
            [
                self.export_srt.get(),
                self.export_txt.get(),
                self.export_vtt.get(),
                self.export_json.get(),
            ]
        ):
            messagebox.showwarning(
                "Warning", "Please select at least one output format!"
            )
            return

        # Create output directories if needed
        if self.separate_folders.get():
            if self.export_srt.get():
                os.makedirs(os.path.join(output_dir, "srt"), exist_ok=True)
            if self.export_vtt.get():
                os.makedirs(os.path.join(output_dir, "vtt"), exist_ok=True)
            if self.export_txt.get():
                os.makedirs(os.path.join(output_dir, "txt"), exist_ok=True)
            if self.export_json.get():
                os.makedirs(os.path.join(output_dir, "json"), exist_ok=True)

        try:
            # Process single file
            if self.mode.get() == 0:
                expected_ext = ".json" if input_format == "json" else ".vtt"
                if not input_path.lower().endswith(expected_ext):
                    messagebox.showwarning(
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
                    messagebox.showwarning(
                        "Warning",
                        f"No {input_format.upper()} files found in the selected directory!",
                    )
                    return

                self.process_directory(
                    input_path, output_dir, target_files, input_format
                )

            self.status_var.set("Conversion completed successfully!")
            self.progress["value"] = 100
            messagebox.showinfo("Success", "Conversion completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {str(e)}")

    def process_single_file(self, input_file, output_dir, input_format):
        self.status_var.set(f"Processing file: {os.path.basename(input_file)}...")
        self.progress["value"] = 0
        self.root.update_idletasks()

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

        self.progress["value"] = 50
        self.root.update_idletasks()

        self.save_output_files(subtitles, output_dir, output_base)
        self.progress["value"] = 100

    def process_directory(self, input_dir, output_dir, target_files, input_format):
        total_files = len(target_files)
        self.status_var.set(f"Processing {total_files} {input_format.upper()} files...")
        self.root.update_idletasks()

        for i, filename in enumerate(target_files):
            try:
                input_file = os.path.join(input_dir, filename)
                self.status_var.set(f"Processing file {i+1}/{total_files}: {filename}")
                self.progress["value"] = (i / total_files) * 100
                self.root.update_idletasks()

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
        strategy = self.naming_strategy.get()
        filename = os.path.basename(input_file)
        base_name = os.path.splitext(filename)[0]

        if strategy == "source":
            return base_name
        elif strategy == "source_with_suffix":
            return f"{base_name}{self.suffix.get()}"
        else:  # custom
            return self.output_name.get()

    def save_output_files(self, subtitles, output_dir, output_base):
        """Save the subtitle files in the selected formats"""
        # SRT format
        if self.export_srt.get():
            srt_content = self.generate_srt(subtitles)
            if self.separate_folders.get():
                srt_dir = os.path.join(output_dir, "srt")
                srt_path = os.path.join(srt_dir, f"{output_base}.srt")
            else:
                srt_path = os.path.join(output_dir, f"{output_base}.srt")

            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

        # VTT format
        if self.export_vtt.get():
            vtt_content = self.generate_vtt(subtitles)
            if self.separate_folders.get():
                vtt_dir = os.path.join(output_dir, "vtt")
                vtt_path = os.path.join(vtt_dir, f"{output_base}.vtt")
            else:
                vtt_path = os.path.join(output_dir, f"{output_base}.vtt")

            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write(vtt_content)

        # Plain text format
        if self.export_txt.get():
            txt_content = self.generate_plain_text(subtitles)
            if self.separate_folders.get():
                txt_dir = os.path.join(output_dir, "txt")
                txt_path = os.path.join(txt_dir, f"{output_base}.txt")
            else:
                txt_path = os.path.join(output_dir, f"{output_base}.txt")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(txt_content)

        # JSON format
        if self.export_json.get():
            json_data = self.generate_json(subtitles)
            if self.separate_folders.get():
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
    root = tk.Tk()
    app = SubtitleConverterApp(root)
    root.mainloop()
