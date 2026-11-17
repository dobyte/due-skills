#!/usr/bin/env python3
"""Build and publish the due-v2 SkillHub package.

Usage:
  python release/skillhub/publish.py --dry-run
  SKILLHUB_KEY=skh_xxx python release/skillhub/publish.py --changelog "v1.1.0"

The script never prints SKILLHUB_KEY. The actual upload is delegated to the
official skillhub CLI (login + publish) against https://api.skillhub.cn.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PACKAGE = BASE / "due-v2"
DEFAULT_HOST = "https://api.skillhub.cn"


def fail(message: str, code: int = 2) -> None:
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(code)


def run(command, secret_index=None) -> None:
    rendered = list(command)
    if secret_index is not None:
        rendered[secret_index] = "***"
    print("+ " + " ".join(rendered))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and publish due-v2 to skillhub.cn")
    parser.add_argument("--dry-run", action="store_true", help="only build and run skillhub metadata validation")
    parser.add_argument("--no-build", action="store_true", help="reuse the existing release/skillhub/due-v2 package")
    parser.add_argument("--changelog", default="", help="changelog text for this version")
    parser.add_argument("--host", default=os.environ.get("SKILLHUB_HOST", DEFAULT_HOST))
    args = parser.parse_args()

    if not args.no_build:
        run([sys.executable, str(BASE / "build.py")])

    if not PACKAGE.is_dir():
        fail("package directory not found: " + str(PACKAGE) + "; run build.py first")

    cli = shutil.which("skillhub")
    if not cli:
        fail(
            "skillhub CLI not found. Install it from https://skillhub.cn/install/skillhub.md "
            "and ensure ~/.local/bin is on PATH."
        )

    if args.dry_run:
        run([cli, "publish", str(PACKAGE), "--host", args.host, "--dry-run", "--json"])
        print("Dry-run passed. No upload was performed.")
        return

    key = os.environ.get("SKILLHUB_KEY", "").strip()
    if not key:
        fail("SKILLHUB_KEY is required for publishing; set it to a skh_ API key")

    # login stores a per-host credential; the key is not echoed by this script.
    run([cli, "login", "--key", key, "--host", args.host], secret_index=3)

    command = [cli, "publish", str(PACKAGE), "--host", args.host, "--json"]
    if args.changelog:
        command.extend(["--changelog", args.changelog])
    run(command)


if __name__ == "__main__":
    main()
