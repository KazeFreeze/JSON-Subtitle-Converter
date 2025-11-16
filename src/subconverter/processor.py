import os
import json
from . import formats # Import from our own package

def get_output_filename(input_file, strategy, custom_name, suffix_text):
    """Determine the output filename based on the naming strategy"""
    filename = os.path.basename(input_file)
    base_name = os.path.splitext(filename)[0]

    if strategy == "source":
        return base_name
    elif strategy == "source_with_suffix":
        return f"{base_name}{suffix_text}"
    else:  # custom
        return custom_name

def save_output_files(subtitles, output_dir, output_base, config):
    """Save the subtitle files in the selected formats"""
    
    def get_path(ext):
        if config["separate_folders"]:
            folder = os.path.join(output_dir, ext)
            os.makedirs(folder, exist_ok=True)
            return os.path.join(folder, f"{output_base}.{ext}")
        else:
            return os.path.join(output_dir, f"{output_base}.{ext}")

    if config["export_srt"]:
        srt_content = formats.generate_srt(subtitles)
        with open(get_path("srt"), "w", encoding="utf-8") as f:
            f.write(srt_content)

    if config["export_vtt"]:
        vtt_content = formats.generate_vtt(subtitles)
        with open(get_path("vtt"), "w", encoding="utf-8") as f:
            f.write(vtt_content)

    if config["export_txt"]:
        txt_content = formats.generate_plain_text(subtitles)
        with open(get_path("txt"), "w", encoding="utf-8") as f:
            f.write(txt_content)

    if config["export_json"]:
        json_data = formats.generate_json(subtitles)
        with open(get_path("json"), "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

def run_conversion(config, progress_callback=None):
    """
    Runs the full conversion process based on a config dictionary.
    
    The progress_callback (if provided) will be called with:
    (current_file_index, total_files, message)
    """
    
    # --- 1. Get all target files ---
    input_path = config["input_path"]
    input_format = config["input_format"]
    extension = f".{input_format}"
    
    target_files = []
    if config["is_directory"]:
        try:
            target_files = [
                os.path.join(input_path, f)
                for f in os.listdir(input_path)
                if f.lower().endswith(extension)
            ]
        except Exception as e:
            raise IOError(f"Could not read directory '{input_path}': {e}")
    else:
        if not input_path.lower().endswith(extension):
            raise ValueError(f"Selected file must be a {input_format.upper()} file!")
        target_files = [input_path]

    if not target_files:
        raise FileNotFoundError(f"No {input_format.upper()} files found.")

    # --- 2. Process each file ---
    total_files = len(target_files)
    for i, input_file in enumerate(target_files):
        filename = os.path.basename(input_file)
        
        if progress_callback:
            progress_callback(i, total_files, f"Processing {i+1}/{total_files}: {filename}")

        try:
            # --- 3. Parse content ---
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            if input_format == "json":
                data = json.loads(content)
                subtitles = formats.convert_json_to_subtitles(data)
            else: # vtt
                subtitles = formats.parse_vtt(content)

            # --- 4. Get output name ---
            output_base = get_output_filename(
                input_file,
                config["naming_strategy"],
                config["custom_name"],
                config["suffix_text"],
            )

            # --- 5. Save all formats ---
            save_output_files(subtitles, config["output_dir"], output_base, config)
        
        except Exception as e:
            # Log and continue with other files
            print(f"Error processing {filename}: {str(e)}")
            if progress_callback:
                progress_callback(i, total_files, f"Error on {filename}: {e}")
            
    if progress_callback:
        progress_callback(total_files, total_files, "Conversion complete!")
