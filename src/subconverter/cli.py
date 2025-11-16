import argparse
import os
from . import processor

def main():
    parser = argparse.ArgumentParser(description="Convert JSON/VTT subtitles.")
    parser.add_argument(
        "input_path",
        help="Path to the input file or directory."
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        dest="output_dir",
        help="Path to the output directory."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "vtt"],
        default="json",
        dest="input_format",
        help="Input file format (default: json)."
    )
    
    # Output formats
    parser.add_argument("--srt", dest="export_srt", action="store_true", help="Export to SRT")
    parser.add_argument("--vtt", dest="export_vtt", action="store_true", help="Export to VTT")
    parser.add_argument("--txt", dest="export_txt", action="store_true", help="Export to TXT")
    parser.add_argument("--json", dest="export_json", action="store_true", help="Export to JSON")

    # Naming
    parser.add_argument(
        "-n", "--naming",
        choices=["source", "custom", "source_with_suffix"],
        default="source",
        dest="naming_strategy",
        help="Output naming strategy (default: source)."
    )
    parser.add_argument(
        "--custom-name",
        default="output",
        help="Custom base name (used if naming='custom')."
    )
    parser.add_argument(
        "--suffix",
        default="_subtitle",
        dest="suffix_text",
        help="Custom suffix (used if naming='source_with_suffix')."
    )
    
    # Flags
    parser.add_argument(
        "-s", "--separate-folders",
        action="store_true",
        help="Save each format in its own sub-folder."
    )
    
    args = parser.parse_args()
    
    # --- Build the config object for the processor ---
    config = vars(args) # Convert argparse.Namespace to dict
    
    # Add extra info
    config["is_directory"] = os.path.isdir(args.input_path)
    
    # Default to exporting SRT if no other format is chosen
    if not any([config["export_srt"], config["export_vtt"], config["export_txt"], config["export_json"]]):
        print("No output format specified. Defaulting to SRT.")
        config["export_srt"] = True
        
    # --- Define a simple callback for CLI progress ---
    def cli_progress(current, total, message):
        percent = (current / total) * 100
        print(f"[{percent:3.0f}%] {message}")

    # --- Run the conversion ---
    try:
        print(f"Starting conversion...")
        processor.run_conversion(config, cli_progress)
        print("Done.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        parser.print_help()

if __name__ == "__main__":
    main()
