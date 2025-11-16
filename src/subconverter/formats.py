import re

def ms_to_srt_time(ms):
    """Convert milliseconds to SRT format time (HH:MM:SS,MMM)"""
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"

def ms_to_vtt_time(ms):
    """Convert milliseconds to VTT format time (HH:MM:SS.MMM)"""
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    seconds, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{ms:03}"

def time_to_ms(time_str):
    """Convert time string to milliseconds (handles SRT/VTT)"""
    time_str = time_str.replace(",", ".")
    parts = time_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    sec_parts = parts[2].split(".")
    seconds = int(sec_parts[0])
    milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
    return hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds

def convert_json_to_subtitles(data):
    """Converts the YouTube JSON structure to an internal list format"""
    subtitles = []
    for event in data.get("events", []):
        if "segs" not in event or not event["segs"]:
            continue
        try:
            start = event.get("tStartMs", 0)
            duration = event.get("dDurationMs", 0)
            end = start + duration
            text = "".join(seg.get("utf8", "") for seg in event["segs"])

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

def parse_vtt(vtt_content):
    """Parse WebVTT format into a list of subtitle dictionaries"""
    subtitles = []
    vtt_content = vtt_content.replace("\r\n", "\n")
    if vtt_content.strip().startswith("WEBVTT"):
        vtt_content = re.sub(r"^WEBVTT.*?\n\n", "", vtt_content, flags=re.DOTALL)

    cue_blocks = re.split(r"\n\n+", vtt_content.strip())
    for block in cue_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue
        timing_line_idx = next(
            (i for i, line in enumerate(lines) if "-->" in line), -1
        )
        if timing_line_idx == -1:
            continue
        timing_match = re.search(
            r"(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)", lines[timing_line_idx]
        )
        if not timing_match:
            continue
        start_time, end_time = timing_match.groups()
        start_ms = time_to_ms(start_time)
        end_ms = time_to_ms(end_time)
        text = "\n".join(lines[timing_line_idx + 1 :])
        subtitles.append({"start": start_ms, "end": end_ms, "text": text})
    return subtitles

def generate_srt(subtitles):
    """Generate SRT format subtitle content"""
    srt = []
    for i, sub in enumerate(subtitles, 1):
        start = ms_to_srt_time(sub["start"])
        end = ms_to_srt_time(sub["end"])
        srt.append(f"{i}\n{start} --> {end}\n{sub['text'].strip()}\n")
    return "\n".join(srt)

def generate_vtt(subtitles):
    """Generate WebVTT format subtitle content"""
    vtt = ["WEBVTT\n"]
    for i, sub in enumerate(subtitles, 1):
        start = ms_to_vtt_time(sub["start"])
        end = ms_to_vtt_time(sub["end"])
        vtt.append(f"\n{i}\n{start} --> {end}\n{sub['text'].strip()}")
    return "\n".join(vtt)

def generate_plain_text(subtitles):
    """Generate plain text from subtitles"""
    return " ".join(sub["text"].strip() for sub in subtitles)

def generate_json(subtitles):
    """Generate simplified JSON format from subtitles"""
    events = []
    for sub in subtitles:
        event = {
            "tStartMs": sub["start"],
            "dDurationMs": sub["end"] - sub["start"],
            "segs": [{"utf8": sub["text"]}],
        }
        events.append(event)
    return {"events": events}
