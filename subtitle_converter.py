import json
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, IntVar, StringVar


class SubtitleConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to Subtitle Converter")
        self.root.geometry("600x480")

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

        self.export_txt = IntVar(value=1)
        ttk.Checkbutton(format_frame, text="Plain Text", variable=self.export_txt).grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )

        self.separate_folders = IntVar(value=0)
        ttk.Checkbutton(
            format_frame,
            text="Use Separate Folders for Each Format",
            variable=self.separate_folders,
        ).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

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
        if self.mode.get() == 0:  # Single file
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
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

        if not input_path:
            messagebox.showwarning(
                "Warning", "Please select an input file or directory!"
            )
            return
        if not output_dir:
            messagebox.showwarning("Warning", "Please select an output directory!")
            return
        if not self.export_srt.get() and not self.export_txt.get():
            messagebox.showwarning(
                "Warning", "Please select at least one output format!"
            )
            return

        # Create output directories if needed
        if self.separate_folders.get():
            if self.export_srt.get():
                os.makedirs(os.path.join(output_dir, "srt"), exist_ok=True)
            if self.export_txt.get():
                os.makedirs(os.path.join(output_dir, "txt"), exist_ok=True)

        try:
            # Process single file
            if self.mode.get() == 0:
                if not input_path.lower().endswith(".json"):
                    messagebox.showwarning(
                        "Warning", "Selected file must be a JSON file!"
                    )
                    return

                self.process_single_file(input_path, output_dir)

            # Process directory (batch)
            else:
                json_files = [
                    f for f in os.listdir(input_path) if f.lower().endswith(".json")
                ]
                if not json_files:
                    messagebox.showwarning(
                        "Warning", "No JSON files found in the selected directory!"
                    )
                    return

                self.process_directory(input_path, output_dir, json_files)

            self.status_var.set("Conversion completed successfully!")
            self.progress["value"] = 100
            messagebox.showinfo("Success", "Conversion completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set(f"Error: {str(e)}")

    def process_single_file(self, input_file, output_dir):
        self.status_var.set(f"Processing file: {os.path.basename(input_file)}...")
        self.progress["value"] = 0
        self.root.update_idletasks()

        # Get output filename
        output_base = self.get_output_filename(input_file)

        # Convert
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        subtitles = self.convert_json_to_subtitles(data)
        self.progress["value"] = 50
        self.root.update_idletasks()

        self.save_output_files(subtitles, output_dir, output_base)
        self.progress["value"] = 100

    def process_directory(self, input_dir, output_dir, json_files):
        total_files = len(json_files)
        self.status_var.set(f"Processing {total_files} JSON files...")
        self.root.update_idletasks()

        for i, filename in enumerate(json_files):
            try:
                input_file = os.path.join(input_dir, filename)
                self.status_var.set(f"Processing file {i+1}/{total_files}: {filename}")
                self.progress["value"] = (i / total_files) * 100
                self.root.update_idletasks()

                # Get output filename
                output_base = self.get_output_filename(input_file)

                # Convert
                with open(input_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                subtitles = self.convert_json_to_subtitles(data)
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

    # Conversion functions
    def ms_to_srt_time(self, ms):
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        seconds, ms = divmod(ms, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

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

    def generate_srt(self, subtitles):
        srt = []
        for i, sub in enumerate(subtitles, 1):
            start = self.ms_to_srt_time(sub["start"])
            end = self.ms_to_srt_time(sub["end"])
            srt.append(f"{i}\n{start} --> {end}\n{sub['text'].strip()}\n")
        return "\n".join(srt)

    def generate_plain_text(self, subtitles):
        return " ".join(sub["text"].strip() for sub in subtitles)


if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleConverterApp(root)
    root.mainloop()
