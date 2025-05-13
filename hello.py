# In free DVR, cannot install scripts. Instead run following in Workspace > Console
# exec(open(r"C:\Users\adg\git\happy-video\hello.py").read()) # shows nothing
# create_simplified_teaser()

import time

# --- CONFIGURATION ---
SOURCE_MEDIA_NAME = "Dave Sands clip.mkv"  # Source media file name
TARGET_TIMELINE_NAME = "Auto Timeline 2"  # Timeline name for this version
VIDEO_TRACK_FOR_CLIPS = 1  # Target video track (1-indexed). 0 or less means no video.
AUDIO_TRACK_FOR_CLIPS = 1  # Target audio track (1-indexed). 0 or less means no audio.

# Clips data: (start_timecode, end_timecode, optional_description)
# These segments are chosen for their standalone impact and clarity.
clips_data = [
    # 1. The Core Benefit and New Perspective
    (
        "0:47",
        "0:52",
        "I think whatever you do it will make you a better programmer because it will give you a different way of thinking about programming.",
    ),
    # 2. The Fundamental Difference of FP
    (
        "1:20",
        "1:36",
        "Functional programming is very different... it's built around the simple concept of mathematical functions and values, and how we build values by applying functions, by composing functions and so on.",
    ),  # Extended slightly for full thought
    # 3. Why Haskell is Chosen (Its Purity and Depth)
    (
        "1:48",
        "2:00",
        "Haskell is in some sense the most functional of the functional programming languages... it's the programming language which is most uncompromising about its view on functional programming.",
    ),
    # 4. A Powerful Tool: Automated Random Testing
    (
        "16:03",
        "16:19",
        "We're going to use a library to do automatic testing for us, or rather to do random testing, generate hundreds perhaps thousands of random values and test the properties for us.",
    ),  # Slightly extended to explain random testing
    # 5. The Appeal and Learning Journey with Haskell
    (
        "2:25",
        "2:42",
        "Even though programs seem very short and beautiful, there are of course lots of ways of doing them, of getting things wrong... so I hope that we will not only learn about functional programming in general but some of the very specific details [of] Haskell.",
    ),  # Shows appeal + realistic learning
]

# Clips data: (start_timecode, end_timecode, optional_description)
# The third element (text content/description) from the original script is ignored here.
clips_data_1 = [
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

# Clips data: (start_timecode, end_timecode, optional_description)
# The third element (text content/description) from the original script is used as the description.
clips_data_0 = [
    # Scene 1: Title & Opening Hook (Visual background)
    ("0:00", "0:03", "Background for Title Overlay"),
    # Scene 2: The "Why This is Different" Hook
    ("0:23", "0:27", "quite a bit more different"),
    ("0:47", "0:52", "make you a better programmer"),
    # Scene 3: The Core Idea – Beyond State
    ("0:59", "1:04", "not based on common imperative/OO idea"),
    ("1:20", "1:26", "built around mathematical functions and values"),
    # Scene 4: Introducing Haskell – The "Pure" Choice
    (
        "1:42",
        "1:48",
        "learn FP through Haskell (says Kestrel)",
    ),  # Note: Original script error, says "Kestrel"
    ("1:48", "1:54", "Haskell is most functional"),
    # ("1:54", "2:00", "most uncompromising"), # Optional part from script, can be added if needed
    # Scene 5: The "Wow" Moment – Automated Testing with QuickCheck
    ("16:03", "16:09", "use a library for automatic testing"),
    ("18:45", "18:47", "QuickCheck failed the test is false (visual)"),
    ("22:15", "22:17", "Fixed property with ~== (visual)"),
    ("22:33", "22:35", "OK, passed 100 tests (visual)"),
    # Scene 6: The Elegance of Recursion
    ("31:00", "31:06", "idea in recursion: solve bigger from smaller"),
    ("34:17", "34:19", "power n 0 = 1 (visual + audio snippet)"),
    (
        "31:50",
        "31:55",
        "n * power n (k-1) (visual + audio snippet 'multiply it by N')",
    ),  # Or "31:33", "31:38" for a clearer code visual
    # Scene 7: The Challenge & Call to Action
    ("37:05", "37:09", "Intersections puzzle slide (visual)"),
    (
        "36:59",
        "37:05",
        "Audio: 'I'd like you to think about this problem...' (for puzzle visual)",
    ),
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
