"""Command-line interface for socialgen."""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="socialgen",
        description="Generate social media carousels from JSON configurations.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate", help="Generate carousel assets.")
    subparsers.add_parser("validate", help="Validate configuration files.")
    subparsers.add_parser("list-modules", help="List available module configs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
