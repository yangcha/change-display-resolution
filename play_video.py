# pylint: disable=invalid-name
"""Play a video using the python-vlc library."""

import sys

import vlc


def play_video(video_path: str, device_name: str = r"\\.\DISPLAY1") -> None:
    """Play a video full-screen on the specified display.

    Args:
        video_path: Path to the video file.
        device_name: Display device name (e.g. r'\\\\.\\DISPLAY1').
    """
    device_name = r"DISPLAY2"  # Example device name, adjust as needed
    instance = vlc.Instance("--qt-fullscreen-screennumber=5")
    player = instance.media_player_new()
    media = instance.media_new(video_path)
    player.set_media(media)
    player.set_fullscreen(True)
    player.play()

    # Wait until playback finishes
    while True:
        state = player.get_state()
        if state in (vlc.State.Ended, vlc.State.Error):
            break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(r"Usage: python play_video.py <video_path> [device_name]")
        print(r"  device_name: e.g. \\.\DISPLAY1 (default), \\.\DISPLAY2")
        sys.exit(1)

    video = sys.argv[1]
    device = sys.argv[2] if len(sys.argv) >= 3 else r"\\.\DISPLAY1"
    play_video(video, device)
