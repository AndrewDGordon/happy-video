# In free DVR, cannot install scripts. Instead run following in Workspace > Console
# exec(open(r"C:\Users\adg\git\happy-video\hello.py").read()) # shows nothing
# create_simplified_teaser()

import time

# --- CONFIGURATION ---
SOURCE_MEDIA_NAME = "Peacemaking - Render 1.mp4"  # Source media file name
TARGET_TIMELINE_NAME = "Append_Teaser_Simplified_V2"  # Timeline name for this version
VIDEO_TRACK_FOR_CLIPS = 1  # Target video track (1-indexed). 0 or less means no video.
AUDIO_TRACK_FOR_CLIPS = 1  # Target audio track (1-indexed). 0 or less means no audio.

# Clips data: (start_timecode, end_timecode, optional_description)
# The third element (text content/description) from the original script is ignored here.
clips_data = [
    ("0:44", "0:49", "Faith & Empowerment Series"),
    ("2:38", "2:45", "Empowering Local Peacebuilders"),
    ("4:55", "5:01", "My Practitioner & Embodied Self"),
    ("7:17", "7:23", "You can't give what you don't have"),
    ("15:15", "15:18", "Show up as ME"),
    ("19:24", "19:30", "Tula Sizwe (Hush, Nation)"),
    ("23:38", "23:44", "There IS Hope!"),
    ("32:41", "32:44", "The Peacebuilder Bird"),
    ("36:03", "36:08", "Empowered to Exemplify"),
    ("56:51", "56:56", "Courage to Name the Unnameable"),
    ("36:56", "37:03", "Peacemaking: A Way of Life"),
]


# --- HELPER FUNCTION ---
def timecode_to_frames(tc_str, frame_rate):
    """Converts timecode string (H:M:S, M:S, or S) to frame count."""
    parts_str = tc_str.split(":")
    s_val, m_val, h_val = 0, 0, 0

    if len(parts_str) == 1:  # Seconds only
        s_val = int(parts_str[0])
    elif len(parts_str) == 2:  # Minutes:Seconds
        m_val = int(parts_str[0])
        s_val = int(parts_str[1])
    elif len(parts_str) == 3:  # Hours:Minutes:Seconds
        h_val = int(parts_str[0])
        m_val = int(parts_str[1])
        s_val = int(parts_str[2])
    else:
        print(f"Error: Invalid timecode format: {tc_str}")
        return 0
    return int((h_val * 3600 + m_val * 60 + s_val) * frame_rate)


# --- MAIN SCRIPT LOGIC ---
def create_simplified_teaser():
    print(f"--- Starting Simplified Teaser Creation using AppendToTimeline ---")

    # Get Resolve objects
    try:
        resolve = app.GetResolve()  # type: ignore
    except NameError:
        print("Error: DaVinci Resolve 'app' object not found.")
        return

    projectManager = resolve.GetProjectManager()
    project = projectManager.GetCurrentProject()
    mediaPool = project.GetMediaPool()

    if not project:
        print("Error: No project open.")
        return
    print(f"Working with project: {project.GetName()}")

    # Find existing timeline or create a new one
    timeline = None
    # Check existing timelines
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == TARGET_TIMELINE_NAME:
            timeline = t
            break

    if timeline:
        print(f"Timeline '{TARGET_TIMELINE_NAME}' exists. Using it.")
        project.SetCurrentTimeline(timeline)
        print(
            f"Warning: Appending to existing timeline '{TARGET_TIMELINE_NAME}'. For a clean slate, clear it manually or use a new target timeline name."
        )
    else:
        print(f"Creating new timeline: {TARGET_TIMELINE_NAME}")
        timeline = mediaPool.CreateEmptyTimeline(TARGET_TIMELINE_NAME)
        if not timeline:
            print(f"Error: Failed to create timeline: {TARGET_TIMELINE_NAME}")
            return
        project.SetCurrentTimeline(timeline)  # Important for new timelines

    if not timeline:
        print("Error: Could not set or create timeline.")
        return

    print(f"Using timeline: {timeline.GetName()}")
    try:
        timeline_frame_rate = float(timeline.GetSetting("timelineFrameRate"))
    except Exception as e:
        print(f"Error getting timeline frame rate: {e}. Defaulting to 24.0 fps.")
        timeline_frame_rate = 24.0
    print(f"Timeline frame rate: {timeline_frame_rate} fps")

    # Find source media item
    source_media_item = None

    rootFolder = mediaPool.GetRootFolder()
    items_in_root = rootFolder.GetClipList()
    if items_in_root:
        for item in items_in_root:
            if item and item.GetName() == SOURCE_MEDIA_NAME:
                source_media_item = item
                break
    if not source_media_item and rootFolder.GetSubFolderList():
        for folder in rootFolder.GetSubFolderList():
            if folder and folder.GetClipList():
                for item_in_sub in folder.GetClipList():
                    if item_in_sub and item_in_sub.GetName() == SOURCE_MEDIA_NAME:
                        source_media_item = item_in_sub
                        break
            if source_media_item:
                break

    if not source_media_item:
        print(f"Error: Source media '{SOURCE_MEDIA_NAME}' not found in Media Pool.")
        return
    print(f"Found source media: {source_media_item.GetName()}")

    # Check if AppendToTimeline is available
    if not callable(getattr(mediaPool, "AppendToTimeline", None)):
        print("Error: mediaPool.AppendToTimeline is not available or not callable.")
        return

    # Process and append clips
    total_clips_to_process = len(clips_data)
    for i, clip_info_tuple in enumerate(clips_data):
        # Unpack, ignoring the third element (description/text)
        start_tc, end_tc = clip_info_tuple[0], clip_info_tuple[1]

        start_frames_source = timecode_to_frames(start_tc, timeline_frame_rate)
        end_frames_source = timecode_to_frames(end_tc, timeline_frame_rate)

        if end_frames_source <= start_frames_source:
            print(
                f"Warning: Clip {i + 1}/{total_clips_to_process} ('{start_tc}' - '{end_tc}') has zero or negative duration. Skipping."
            )
            continue

        print(
            f"Processing clip {i + 1}/{total_clips_to_process}: Source In {start_tc} Out {end_tc}"
        )

        clipInfo = {
            "mediaPoolItem": source_media_item,
            "startFrame": start_frames_source,
            "endFrame": end_frames_source - 1,
        }
        print(f"  Clip: {clipInfo}")

        appended_timeline_items = mediaPool.AppendToTimeline([clipInfo])
        if not appended_timeline_items:
            print(
                f"Error: Failed to append clip {i + 1}/{total_clips_to_process} to timeline."
            )
            continue
        time.sleep(0.4)  # Short pause for stability, adjust if necessary

    print(
        f"\n--- Simplified teaser creation complete for timeline: '{timeline.GetName()}' ---"
    )
    print("Please review the timeline for the appended clip segments.")


# --- HOW TO RUN ---
# 1. Open DaVinci Resolve.
# 2. Open your project and ensure the source media (e.g., "Peacemaking - Render 1.mp4") is in the Media Pool.
# 3. Go to Workspace > Console.
# 4. In the console, ensure you are in the 'Py3' environment.
# 5. Paste this entire script into the console and press Enter.
# 6. Then, type the following command and press Enter:
# create_simplified_teaser()
