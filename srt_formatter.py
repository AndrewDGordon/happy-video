def format_transcript_as_srt(transcript_data):
    """
    Formats the transcript data into SRT (SubRip Text) format.
    """
    if not transcript_data:
        return ""

    def format_time(seconds):
        millis = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        minutes = seconds // 60
        seconds %= 60
        hours = minutes // 60
        minutes %= 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

    srt_output = []
    for i, segment in enumerate(transcript_data):
        # Handle both dictionary and object formats
        if hasattr(segment, 'start'):
            start = segment.start
            duration = segment.duration
            text = segment.text
        else:
            start = segment["start"]
            duration = segment["duration"]
            text = segment["text"]
            
        start_time = format_time(start)
        end_time = format_time(start + duration)
        srt_output.append(f"{i + 1}\n{start_time} --> {end_time}\n{text}\n")
    return "\n".join(srt_output)
