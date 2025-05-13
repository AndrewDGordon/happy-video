from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
import re  # For extracting video ID from URL


def extract_video_id(url_or_id):
    """
    Extracts the YouTube video ID from a URL or returns the ID if it's already an ID.
    Handles various YouTube URL formats.
    """
    # Regex to find video ID from different YouTube URL formats
    # 1. Standard: https://www.youtube.com/watch?v=VIDEO_ID
    # 2. Shortened: https://youtu.be/VIDEO_ID
    # 3. Embed: https://www.youtube.com/embed/VIDEO_ID
    # 4. With other params: https://www.youtube.com/watch?v=VIDEO_ID&feature=youtu.be
    # 5. Live: https://www.youtube.com/live/VIDEO_ID?feature=share
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/live\/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # If it doesn't match any URL pattern, assume it's a raw video ID
    # A typical YouTube video ID is 11 characters long and contains letters, numbers, hyphens, and underscores.
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url_or_id):
        return url_or_id

    return None  # Return None if no valid ID is found


def get_youtube_transcript(video_id_or_url, languages=["en", "en-US"]):
    """
    Fetches the transcript for a given YouTube video ID or URL.

    Args:
        video_id_or_url (str): The YouTube video ID or URL.
        languages (list, optional): A list of preferred language codes (e.g., ['en', 'es', 'de']).
                                    The API will try to fetch these in order.
                                    Defaults to ['en', 'en-US'].

    Returns:
        list: A list of dictionaries, where each dictionary represents a segment
              of the transcript with 'text', 'start', and 'duration' keys.
              Returns None if the transcript cannot be fetched.
    """
    video_id = extract_video_id(video_id_or_url)
    if not video_id:
        print(f"Error: Could not extract a valid video ID from '{video_id_or_url}'.")
        print("Please provide a valid YouTube video URL or an 11-character video ID.")
        return None

    try:
        # Fetch available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to find a transcript in the preferred languages
        transcript = None
        for lang_code in languages:
            try:
                transcript = transcript_list.find_transcript([lang_code])
                print(f"Found transcript in '{lang_code}'.")
                break
            except NoTranscriptFound:
                continue  # Try next language

        # If no preferred language transcript is found, try to get any available one
        if not transcript:
            print(f"No transcript found in preferred languages: {languages}.")
            print("Attempting to fetch the first available transcript...")
            try:
                # transcript_list is an iterable of Transcript objects
                # We can iterate through it to find the first available one
                available_transcripts = list(
                    transcript_list
                )  # Convert to list to check if empty
                if available_transcripts:
                    first_available = available_transcripts[0]
                    transcript = first_available
                    print(
                        f"Found transcript in '{first_available.language_code}' (language: {first_available.language})."
                    )
                else:
                    print(f"No transcripts available at all for video ID: {video_id}")
                    return None
            except Exception as e:  # Catch any other potential errors during fallback
                print(
                    f"Error fetching fallback transcript for video ID {video_id}: {e}"
                )
                return None

        # Fetch the actual transcript data (list of dictionaries)
        transcript_data = transcript.fetch()
        return transcript_data

    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video ID: {video_id}")
        return None
    except (
        NoTranscriptFound
    ):  # This might be redundant due to the loop, but good for specific cases
        print(
            f"No transcript found for video ID: {video_id} in any of the specified or available languages."
        )
        return None
    except VideoUnavailable:
        print(f"Video {video_id} is unavailable (private, deleted, etc.).")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for video ID {video_id}: {e}")
        return None


def format_transcript_as_text(transcript_data):
    """
    Formats the transcript data into a single string.
    """
    if not transcript_data:
        return ""
    return " ".join(
        [
            str(segment.text) if hasattr(segment, "text") else segment["text"]
            for segment in transcript_data
        ]
    )


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
        if hasattr(segment, "start"):
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


if __name__ == "__main__":
    # Example Usage:
    video_input = input("Enter YouTube Video URL or ID: ")
    # video_input = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Astley
    # video_input = "https://www.youtube.com/watch?v=h06WOB_2tY4" # Example with German transcript
    # video_input = "jNQXAC9IVRw" # Kurzgesagt - No English, but other languages
    # video_input = "non_existent_video_id"
    # video_input = "https://www.youtube.com/watch?v=video_with_transcripts_disabled" (find one)

    # You can specify preferred languages
    # transcript_data = get_youtube_transcript(video_input, languages=['en', 'es', 'de', 'fr'])
    transcript_data = get_youtube_transcript(video_input)  # Defaults to English

    if transcript_data:
        # Option 1: Plain text
        plain_text = format_transcript_as_text(transcript_data)
        print("\n--- Plain Text Transcript ---")
        print(plain_text)

        # Save plain text to a file
        video_id_for_filename = extract_video_id(video_input) or "transcript"
        text_filename = f"{video_id_for_filename}_transcript.txt"
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(plain_text)
        print(f"\nPlain text transcript saved to {text_filename}")

        # Option 2: SRT format
        srt_text = format_transcript_as_srt(transcript_data)
        print("\n--- SRT Transcript ---")
        # print(srt_text) # Can be very long, so maybe just save it

        # Save SRT to a file
        srt_filename = f"{video_id_for_filename}_transcript.srt"
        with open(srt_filename, "w", encoding="utf-8") as f:
            f.write(srt_text)
        print(f"SRT transcript saved to {srt_filename}")

    else:
        print("Failed to retrieve transcript.")
