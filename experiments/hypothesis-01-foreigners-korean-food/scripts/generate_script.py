"""Generate Korean documentary script from foreign Reddit posts.

Usage: python generate_script.py <video_id>
Reads:  videos/{video_id}/sources.json
Writes: videos/{video_id}/script.json, videos/{video_id}/script.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = ROOT / "prompts" / "script_generation.md"
VIDEOS_DIR = ROOT / "videos"
MODEL = "claude-opus-4-6"
MAX_TOKENS = 4000


def load_sources(video_id: str) -> list[dict]:
    src = VIDEOS_DIR / video_id / "sources.json"
    if not src.exists():
        sys.exit(f"sources.json not found: {src}")
    data = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 3:
        sys.exit(f"sources.json must be a list of exactly 3 items, got {len(data) if isinstance(data, list) else type(data).__name__}")
    return data


def format_sources(sources: list[dict]) -> str:
    return "\n\n".join(
        f"### Source {i + 1}\nURL: {s.get('url', '')}\nTitle: {s.get('title', '')}\n\n{s['content']}"
        for i, s in enumerate(sources)
    )


def extract_json(text: str) -> dict:
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]
    return json.loads(text.strip())


def generate(client: Anthropic, system_prompt: str, sources: list[dict]) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": format_sources(sources)}],
    )
    return extract_json(msg.content[0].text)


def write_outputs(video_id: str, result: dict) -> None:
    out_dir = VIDEOS_DIR / video_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if "error" in result:
        (out_dir / "script_error.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        sys.exit(f"Claude rejected sources: {result['error']}")

    (out_dir / "script.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    plain = "\n\n".join([
        result["hook"],
        *[s["narration"] for s in result["stories"]],
        result["outro"],
    ])
    (out_dir / "script.txt").write_text(plain, encoding="utf-8")
    print(f"wrote script.json + script.txt → videos/{video_id}/")
    print(f"next: paste script.txt into TypeCast, save audio as videos/{video_id}/audio.mp3")


def main() -> None:
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY not set in .env")

    client = Anthropic(api_key=api_key)
    sources = load_sources(args.video_id)
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8")
    result = generate(client, system_prompt, sources)
    write_outputs(args.video_id, result)


if __name__ == "__main__":
    main()
