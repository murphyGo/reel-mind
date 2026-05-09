"""Command line entrypoint for Reel-Mind operator smoke checks."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from reel_mind.foundation.bootstrap import Runtime, build_runtime


def main(argv: Sequence[str] | None = None, runtime: Runtime | None = None) -> int:
    parser = argparse.ArgumentParser(prog="reel-mind")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("list-active-channels")

    validate = subcommands.add_parser("validate-channel-config")
    validate.add_argument("channel_id")

    args = parser.parse_args(argv)
    active_runtime = runtime or build_runtime(service="reel-mind/cli")

    if args.command == "list-active-channels":
        for channel_id in active_runtime.config_loader.list_active_channels():
            print(channel_id)
        return 0

    if args.command == "validate-channel-config":
        config = active_runtime.config_loader.load_channel_config(args.channel_id)
        print(config.version_hash)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
