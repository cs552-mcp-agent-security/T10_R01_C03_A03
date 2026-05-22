"""vidpack — profile-driven FFmpeg wrapper CLI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import profiles, runner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vidpack")
    parser.add_argument("--version", action="version", version="vidpack 0.1.0")
    parser.add_argument("profile", help="Profile name defined in profiles.toml")
    parser.add_argument("input", help="Path to input media file")
    parser.add_argument("-o", "--output", help="Output path (default: derived from input + profile container)")
    parser.add_argument("--dry-run", action="store_true", help="Print the ffmpeg command without running it")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profile = profiles.load_profile(args.profile)
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.with_suffix(f".{profile['container']}")

    if output_path.exists() and not args.dry_run:
        print(f"error: output {output_path} already exists; refusing to overwrite", file=sys.stderr)
        return 2

    cmds = runner.build_ffmpeg_command(profile, input_path, output_path)
    if args.dry_run:
        for c in cmds:
            print(" ".join(c))
        return 0
    return runner.run(cmds)


if __name__ == "__main__":
    sys.exit(main())
