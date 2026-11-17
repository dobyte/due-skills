#!/usr/bin/env python3
"""Bump the due-v2 version for the automatic SkillHub release workflow.

The version is stored in both:
  - skills/due-v2/SKILL.md
  - release/skillhub/SKILL.template

Modes:
  auto  - keep the current version if HEAD already changed it, otherwise bump patch
  none  - keep the current version
  patch / minor / major - force the corresponding bump

The script prints only the resulting version to stdout; diagnostics go to stderr.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
MAIN_SKILL = REPO / "skills" / "due-v2" / "SKILL.md"
TEMPLATE = BASE / "SKILL.template"
VERSION_RE = re.compile(r"(?m)^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$")


def fail(message: str) -> None:
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(2)


def read_version(path: Path) -> str:
    if not path.is_file():
        fail("file not found: " + str(path))
    match = VERSION_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        fail("version not found in " + str(path))
    return match.group(1)


def write_version(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = VERSION_RE.subn("version: " + version, text, count=1)
    if count != 1:
        fail("version not found in " + str(path))
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(updated)


def bump(version: str, part: str) -> str:
    major, minor, patch = (int(item) for item in version.split("."))
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        fail("unsupported bump part: " + part)
    return "%d.%d.%d" % (major, minor, patch)


def previous_version() -> str:
    relative = MAIN_SKILL.relative_to(REPO).as_posix()
    try:
        output = subprocess.check_output(
            ["git", "show", "HEAD^:" + relative],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
        ).decode("utf-8", errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    match = VERSION_RE.search(output)
    return match.group(1) if match else ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump due-v2 SkillHub version")
    parser.add_argument("--mode", choices=["auto", "none", "patch", "minor", "major"], default="auto")
    parser.add_argument("--dry-run", action="store_true", help="print the target version without writing")
    args = parser.parse_args()

    main_version = read_version(MAIN_SKILL)
    template_version = read_version(TEMPLATE)
    if main_version != template_version:
        fail(
            "version mismatch: skills/due-v2/SKILL.md=%s, release/skillhub/SKILL.template=%s"
            % (main_version, template_version)
        )

    if args.mode == "none":
        target = main_version
    elif args.mode == "auto":
        previous = previous_version()
        if previous and previous != main_version:
            print(
                "HEAD already changed version %s -> %s; keeping it"
                % (previous, main_version),
                file=sys.stderr,
            )
            target = main_version
        else:
            target = bump(main_version, "patch")
    else:
        target = bump(main_version, args.mode)

    if not args.dry_run and target != main_version:
        write_version(MAIN_SKILL, target)
        write_version(TEMPLATE, target)

    print(target)


if __name__ == "__main__":
    main()
