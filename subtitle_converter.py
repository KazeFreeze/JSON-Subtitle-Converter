import json
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class SubtitleConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to Subtitle Converter")
        
        # Input File Selection
        ttk.Label(root, text="Input JSON File:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.input_path = tk.StringVar()
        ttk.Entry(root, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(root, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5, pady=5)
        
        # Output Directory Selection
        ttk.Label(root, text="Output Directory:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.output_dir = tk.StringVar()
        ttk.Entry(root, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(root, text="Browse", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)
        
        # Output File Name
        ttk.Label(root, text="Output Base Name:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.output_name = tk.StringVar(value="output")
        ttk.Entry(root, textvariable=self.output_name, width=50).grid(row=2, column=1, padx=5, pady=5)
        
        # Convert Button
        ttk.Button(root, text="Convert", command=self.convert).grid(row=3, column=1, pady=10)
        
        # Status Label
        self.status = ttk.Label(root, text="", foreground="red")
        self.status.grid(row=4, column=0, columnspan=3, pady=5)

    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.input_path.set(file_path)

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.output_dir.set(dir_path)

    def convert(self):
        input_file = self.input_path.get()
        output_dir = self.output_dir.get()
        base_name = self.output_name.get()
        
        if not input_file:
            self.status.config(text="Please select an input file!")
            return
        if not output_dir:
            self.status.config(text="Please select an output directory!")
            return
        if not base_name:
            self.status.config(text="Please enter a base name for output files!")
            return
        
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            subtitles = self.convert_json_to_subtitles(data)
            
            srt_path = f"{output_dir}/{base_name}.srt"
            txt_path = f"{output_dir}/{base_name}.txt"
            
            with open(srt_path, 'w') as f:
                f.write(self.generate_srt(subtitles))
            
            with open(txt_path, 'w') as f:
                f.write(self.generate_plain_text(subtitles))
            
            messagebox.showinfo("Success", f"Files created successfully:\n{srt_path}\n{txt_path}")
            self.status.config(text="")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.status.config(text=f"Error: {str(e)}")

    # Existing conversion functions from previous code
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
                  subtitles.append({
                      "start": start,
                      "end": end,
                      "text": text
                  })
                  
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