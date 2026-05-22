"""Build and execute ffmpeg subprocess calls based on a profile dict."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path


def build_ffmpeg_command(profile: dict, input_path: Path, output_path: Path) -> list[list[str]]:
    """Translate a profile dict into one or more ffmpeg argv lists.

    All profile paths now return a list of commands (the gif path needs
    two passes: palettegen then paletteuse).
    """
    container = profile["container"]
    if container == "gif":
        fps = profile.get("fps", 12)
        scale = profile.get("scale", "480:-1")
        palette = Path(tempfile.mkdtemp()) / "palette.png"
        pass1 = ["ffmpeg", "-i", str(input_path),
                 "-vf", f"fps={fps},scale={scale}:flags=lanczos,palettegen",
                 str(palette)]
        pass2 = ["ffmpeg", "-i", str(input_path), "-i", str(palette),
                 "-lavfi", f"fps={fps},scale={scale}:flags=lanczos[x];[x][1:v]paletteuse",
                 str(output_path)]
        return [pass1, pass2]

    cmd = ["ffmpeg", "-i", str(input_path),
           "-c:v", profile["video_codec"], "-c:a", profile["audio_codec"]]
    if "video_bitrate" in profile:
        cmd += ["-b:v", profile["video_bitrate"]]
    if "crf" in profile:
        cmd += ["-crf", str(profile["crf"])]
    scale = profile.get("scale")
    if scale and scale != "source":
        cmd += ["-vf", f"scale={scale}"]
    cmd.append(str(output_path))
    return [cmd]


def run(cmds: list[list[str]]) -> int:
    for c in cmds:
        rc = subprocess.call(c)
        if rc != 0:
            return rc
    return 0
