# Script to run in DaVinci Resolve Console, using AppendToTimeline and adding gaps
# Updated SOURCE_MEDIA_NAME

import time

# --- CONFIGURATION ---
SOURCE_MEDIA_NAME = "Peacemaking - Render 1.mp4"  # <<<< UPDATED
TARGET_TIMELINE_NAME = "Append_Teaser_Gaps_MP4_V1"  # Adjusted for new run
VIDEO_TRACK_FOR_CLIPS = 1
AUDIO_TRACK_FOR_CLIPS = 1
TEXT_TRACK_INDEX = 2
DEFAULT_TEXT_DURATION_FRAMES = 120

GAP_DURATION_SECONDS = 1.0  # Duration of the gap between clips in seconds

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
    parts = list(map(int, tc_str.split(":")))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h = 0
        m, s = parts
    else:
        print(f"Error: Invalid timecode format: {tc_str}")
        return 0
    return int((h * 3600 + m * 60 + s) * frame_rate)


# --- MAIN SCRIPT LOGIC ---
def create_teaser_with_gaps_mp4():  # Renamed function slightly for clarity
    print(
        "--- Starting Teaser Creation with Gaps (MP4 Source) using AppendToTimeline ---"
    )

    resolve = app.GetResolve()
    projectManager = resolve.GetProjectManager()
    project = projectManager.GetCurrentProject()
    mediaPool = project.GetMediaPool()
    fusion = resolve.Fusion()

    if not project:
        print("Error: No project open.")
        return
    print(f"Working with project: {project.GetName()}")

    existing_timeline = None
    for i in range(1, project.GetTimelineCount() + 1):
        t = project.GetTimelineByIndex(i)
        if t and t.GetName() == TARGET_TIMELINE_NAME:
            existing_timeline = t
            break

    if existing_timeline:
        print(f"Timeline '{TARGET_TIMELINE_NAME}' exists. Using it.")
        timeline = existing_timeline
        project.SetCurrentTimeline(timeline)
        print(
            "Warning: Appending to existing timeline. Clear manually or use new name for clean slate."
        )
    else:
        print(f"Creating new timeline: {TARGET_TIMELINE_NAME}")
        timeline = mediaPool.CreateEmptyTimeline(TARGET_TIMELINE_NAME)
        if not timeline:
            print(f"Error: Failed to create timeline: {TARGET_TIMELINE_NAME}")
            return
        project.SetCurrentTimeline(timeline)

    if not timeline:
        print("Error: Could not set/create timeline.")
        return
    print(f"Using timeline: {timeline.GetName()}")
    try:
        timeline_frame_rate = float(timeline.GetSetting("timelineFrameRate"))
    except:
        print("Error getting timeline FPS. Defaulting to 24.0")
        timeline_frame_rate = 24.0
    print(f"Timeline frame rate: {timeline_frame_rate} fps")

    gap_duration_frames = int(GAP_DURATION_SECONDS * timeline_frame_rate)
    print(
        f"Gap duration: {GAP_DURATION_SECONDS} seconds ({gap_duration_frames} frames)"
    )

    source_media_item = None
    rootFolder = mediaPool.GetRootFolder()
    items = rootFolder.GetClipList()
    if items:
        for item in items:
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
        print(f"Error: Source media '{SOURCE_MEDIA_NAME}' not found.")
        return
    print(f"Found source media: {source_media_item.GetName()}")

    max_video_track_needed = max(VIDEO_TRACK_FOR_CLIPS, TEXT_TRACK_INDEX)
    while timeline.GetTrackCount("video") < max_video_track_needed:
        if not timeline.AddTrack("video"):
            print("Error: Failed to add video track.")
            return
        time.sleep(0.1)
    while timeline.GetTrackCount("audio") < AUDIO_TRACK_FOR_CLIPS:
        if not timeline.AddTrack("audio"):
            print("Error: Failed to add audio track.")
            return
        time.sleep(0.1)
    print(
        f"Video tracks: {timeline.GetTrackCount('video')}, Audio tracks: {timeline.GetTrackCount('audio')}"
    )

    if not callable(mediaPool.AppendToTimeline):
        print("Error: mediaPool.AppendToTimeline not callable.")
        return

    current_timeline_write_pos_frames = timeline.GetEndFrame()
    if current_timeline_write_pos_frames is None:
        start_frame_setting = timeline.GetSetting("timelineStartFrame")
        current_timeline_write_pos_frames = (
            int(start_frame_setting) if start_frame_setting else 0
        )

    total_clips = len(clips_data)
    for i, (start_tc, end_tc, text_content) in enumerate(clips_data):
        start_frames_source = timecode_to_frames(start_tc, timeline_frame_rate)
        end_frames_source = timecode_to_frames(end_tc, timeline_frame_rate)
        clip_segment_duration_frames = end_frames_source - start_frames_source

        if clip_segment_duration_frames <= 0:
            print(
                f"Warning: Clip {i + 1} ('{start_tc}'-'{end_tc}') has zero/negative duration. Skipping."
            )
            continue

        print(f"Processing clip {i + 1}/{total_clips}: Source {start_tc}-{end_tc}")

        clip_to_append_info = {
            "mediaPoolItem": source_media_item,
            "startFrame": start_frames_source,
            "endFrame": end_frames_source - 1,
        }
        print(f"  Attempting to append content clip: {clip_to_append_info}")
        appended_content_items = mediaPool.AppendToTimeline([clip_to_append_info])
        time.sleep(0.3)

        if appended_content_items:
            print(f"    Content clip appended. Items: {appended_content_items}")
            actual_content_clip_on_timeline = (
                appended_content_items[0] if appended_content_items else None
            )

            if actual_content_clip_on_timeline:
                if text_content:
                    text_record_frame = current_timeline_write_pos_frames
                    print(
                        f"    Adding text: '{text_content}' at timeline frame {text_record_frame}"
                    )
                    text_title_params = {
                        "trackIndex": TEXT_TRACK_INDEX,
                        "recordFrame": text_record_frame,
                        "duration": min(
                            clip_segment_duration_frames, DEFAULT_TEXT_DURATION_FRAMES
                        ),
                    }
                    text_timeline_item = None
                    generator_list = fusion.GetToolList("Generator") if fusion else None
                    if generator_list and "TextPlus" in generator_list:
                        text_timeline_item = timeline.InsertGeneratorIntoTimeline(
                            "TextPlus", text_title_params
                        )
                    else:
                        text_timeline_item = timeline.InsertTitleIntoTimeline(
                            "Text+", text_title_params
                        )
                    time.sleep(0.3)

                    if text_timeline_item:
                        comp = text_timeline_item.GetFusionCompByIndex(1)
                        if comp:
                            tools = comp.GetToolList(False)
                            text_tool = None
                            if tools:
                                for tid in list(tools.keys()):
                                    t = tools.get(tid)
                                    if (
                                        t
                                        and t.GetAttrs().get("TOOLS_RegID")
                                        == "TextPlus"
                                    ):
                                        text_tool = t
                                        break
                            if text_tool:
                                text_tool.SetInput("StyledText", text_content, 0)
                                print(f"      Text set.")
                            else:
                                print(f"    Warning: TextPlus tool not found for text.")
                        else:
                            print(f"    Warning: FusionComp not found for text.")
                    else:
                        print(f"    Warning: Failed to insert text title.")

                current_timeline_write_pos_frames += clip_segment_duration_frames
            else:
                print(
                    f"  Warning: Content clip appended but couldn't get TimelineItem."
                )
                current_timeline_write_pos_frames += clip_segment_duration_frames
        else:
            print(f"  Failed to append content clip {i + 1}.")
            current_timeline_write_pos_frames += clip_segment_duration_frames

        if i < total_clips - 1 and gap_duration_frames > 0:
            print(f"  Adding gap of {gap_duration_frames} frames.")
            gap_record_frame = current_timeline_write_pos_frames

            slug_params = {
                "trackIndex": VIDEO_TRACK_FOR_CLIPS,
                "recordFrame": gap_record_frame,
                "duration": gap_duration_frames,
            }
            black_slug_item = None
            generator_name_to_try = "Solid Color"
            if (
                fusion
                and fusion.GetToolList("Generator")
                and generator_name_to_try in fusion.GetToolList("Generator")
            ):
                black_slug_item = timeline.InsertGeneratorIntoTimeline(
                    generator_name_to_try, slug_params
                )
                if black_slug_item:
                    comp = black_slug_item.GetFusionCompByIndex(1)
                    if comp:
                        tools = comp.GetToolList(False)
                        solid_color_tool = None
                        if tools:
                            for tid in list(tools.keys()):
                                t = tools.get(tid)
                                if t and (
                                    t.GetAttrs().get("TOOLS_RegID") == "Background"
                                    or t.GetAttrs().get("TOOLS_RegID") == "SolidColor"
                                ):
                                    solid_color_tool = t
                                    break
                        if solid_color_tool:
                            if "TopLeftRed" in solid_color_tool.GetInputList():
                                solid_color_tool.SetInput("TopLeftRed", 0.0, 0)
                                solid_color_tool.SetInput("TopLeftGreen", 0.0, 0)
                                solid_color_tool.SetInput("TopLeftBlue", 0.0, 0)
                                solid_color_tool.SetInput("TopLeftAlpha", 1.0, 0)
                                print(f"    Gap (Solid Color set to black) added.")
                            elif hasattr(solid_color_tool, "Color") and hasattr(
                                solid_color_tool.Color, "Red"
                            ):  # Check for grouped color
                                solid_color_tool.Color.Red = 0.0
                                solid_color_tool.Color.Green = 0.0
                                solid_color_tool.Color.Blue = 0.0
                                solid_color_tool.Color.Alpha = 1.0  # Ensure opaque
                                print(
                                    f"    Gap (Solid Color set to black via Color group) added."
                                )
                            else:
                                print(
                                    f"    Warning: Could not set color for '{generator_name_to_try}'."
                                )
                        else:
                            print(
                                f"    Warning: Tool not found within '{generator_name_to_try}'."
                            )
                    else:
                        print(f"    Warning: FusionComp not found for gap slug.")
                else:
                    print(f"    Failed to insert '{generator_name_to_try}' for gap.")
            else:
                print(
                    f"    Warning: Generator '{generator_name_to_try}' not found. Skipping gap."
                )

            if black_slug_item:
                current_timeline_write_pos_frames += gap_duration_frames
            else:
                print(f"    Failed to add gap after clip {i + 1}.")

    print(f"\n--- Teaser with gaps (MP4) attempt complete: '{timeline.GetName()}' ---")
    print("Review timeline for clip segments, gaps, and text placement.")


# --- To Run ---
# Paste into Resolve console (Workspace > Console, Py3)
# Then type:
# create_teaser_with_gaps_mp4()
