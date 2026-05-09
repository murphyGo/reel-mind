"""Assemble final 9:16 short from script.json + audio.mp3 + Pexels stock clips.

Usage: python assemble_video.py <video_id>
Requires: videos/{video_id}/script.json, videos/{video_id}/audio.mp3
Writes:   videos/{video_id}/final.mp4, videos/{video_id}/subtitles.srt
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = ROOT / "videos"
PEXELS_API = "https://api.pexels.com/videos/search"


def get_audio_duration(audio: Path) -> float:
    out = subprocess.check_output([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio),
    ])
    return float(out.strip())


def fetch_pexels_clip(query: str, api_key: str, out_path: Path) -> None:
    r = requests.get(
        PEXELS_API,
        headers={"Authorization": api_key},
        params={"query": query, "orientation": "portrait", "size": "medium", "per_page": 5},
        timeout=30,
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        raise RuntimeError(f"no Pexels results for query: {query}")
    files = sorted(videos[0]["video_files"], key=lambda f: f.get("width", 0))
    chosen = next((f for f in files if f.get("width", 0) >= 720), files[-1])
    with requests.get(chosen["link"], stream=True, timeout=120) as resp:
        resp.raise_for_status()
        out_path.write_bytes(resp.content)


def fmt_srt_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


def build_srt(script: dict, total_duration: float, out: Path) -> None:
    """Allocate subtitle timing proportional to character count."""
    segments: list[tuple[str, str]] = [
        ("hook", script["hook"]),
        *[(f"story_{i + 1}", s["narration"]) for i, s in enumerate(script["stories"])],
        ("outro", script["outro"]),
    ]
    total_chars = sum(len(t) for _, t in segments) or 1
    cursor = 0.0
    blocks = []
    for idx, (_label, text) in enumerate(segments, start=1):
        dur = total_duration * (len(text) / total_chars)
        start, end = cursor, cursor + dur
        blocks.append(f"{idx}\n{fmt_srt_time(start)} --> {fmt_srt_time(end)}\n{text}\n")
        cursor = end
    out.write_text("\n".join(blocks), encoding="utf-8")


def assemble(video_dir: Path, clips: list[Path], audio: Path, srt: Path, out: Path) -> None:
    concat_file = video_dir / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{c.resolve()}'" for c in clips), encoding="utf-8"
    )
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"subtitles={srt.resolve()}:force_style='FontName=NanumGothic,FontSize=18,Outline=2,Alignment=2'"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio),
        "-vf", vf,
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    args = parser.parse_args()

    vdir = VIDEOS_DIR / args.video_id
    script_path = vdir / "script.json"
    audio = vdir / "audio.mp3"

    if not script_path.exists():
        sys.exit(f"script.json missing — run generate_script.py {args.video_id} first")
    if not audio.exists():
        sys.exit(f"audio.mp3 missing — paste script.txt into TypeCast and save audio at {audio}")

    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        sys.exit("PEXELS_API_KEY not set in .env")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    duration = get_audio_duration(audio)

    srt = vdir / "subtitles.srt"
    build_srt(script, duration, srt)

    clips_dir = vdir / "clips"
    clips_dir.mkdir(exist_ok=True)
    clips: list[Path] = []
    queries = script.get("visual_queries") or ["korean food"]
    for i, query in enumerate(queries):
        clip_path = clips_dir / f"clip_{i:02d}.mp4"
        if not clip_path.exists():
            print(f"fetching Pexels clip {i + 1}/{len(queries)}: {query}")
            fetch_pexels_clip(query, api_key, clip_path)
        clips.append(clip_path)

    out = vdir / "final.mp4"
    print(f"assembling {len(clips)} clips + {duration:.1f}s audio → {out}")
    assemble(vdir, clips, audio, srt, out)
    print(f"done: {out}")


if __name__ == "__main__":
    main()
