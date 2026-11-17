#!/usr/bin/env python3
"""Build the skillhub.cn release package for due-v2.

The package is generated from:
  - release/skillhub/SKILL.template.md
  - skills/due-v2/references/**/*.md

It validates the skillhub.cn constraints (frontmatter, file types, file count,
per-file/total size, local links) and writes due-v2-<version>.zip.
"""

import os
import re
import shutil
import sys
import urllib.parse
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
SRC = REPO / "skills" / "due-v2"
REFS = SRC / "references"
TEMPLATE = BASE / "SKILL.template"
OUT = BASE / "due-v2"

ALLOWED_EXT = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".js", ".cjs", ".mjs",
    ".ts", ".py", ".sh", ".png", ".jpg", ".svg",
}
MAX_FILES = 100
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 10 * 1024 * 1024
SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def die(message: str) -> None:
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(1)


def parse_frontmatter(text: str) -> dict:
    """Parse the simple flat frontmatter accepted by the skillhub.cn CLI.

    Only key: value and key: [a, b] forms are supported. Nested blocks and
    dash lists are rejected on purpose: the official CLI does not parse them.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        die("SKILL.template.md must start with ---")
    end = -1
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end < 0:
        die("SKILL.template.md frontmatter is missing the closing ---")

    data = {}
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            die("unsupported frontmatter line (no colon): " + line)
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [
                item.strip().strip("'\"")
                for item in inner.split(",")
                if item.strip()
            ] if inner else []
        else:
            data[key] = value.strip("'\"")
    return data


def validate_metadata(meta: dict) -> None:
    slug = str(meta.get("slug", "")).strip()
    version = str(meta.get("version", "")).strip()
    display_name = str(meta.get("displayName", "")).strip()

    if not slug:
        die("frontmatter is missing slug")
    if not SLUG_RE.match(slug):
        die("slug must be kebab-case: " + slug)
    if not 2 <= len(slug) <= 128:
        die("slug length must be 2-128: " + slug)
    if not version:
        die("frontmatter is missing version")
    if not SEMVER_RE.match(version):
        die("version is not valid SemVer: " + version)
    if not display_name:
        die("frontmatter is missing displayName")
    if len(display_name) > 200:
        die("displayName is longer than 200 characters")
    if "metadata" in meta:
        die("nested metadata blocks are not parsed by the skillhub.cn CLI")
    if not str(meta.get("description", "")).strip():
        die("frontmatter is missing description")

    tags = meta.get("tags")
    if tags is not None and not isinstance(tags, list):
        die("tags must use the inline form: tags: [a, b, c]")

    summary = str(meta.get("summary", "")).strip()
    if len(summary) > 200:
        die("summary is longer than 200 characters")


def validate_local_links(root: Path) -> None:
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if re.search(r"\[[^\]]*\]\((?:\.\.?/)?examples/", text):
            die("local examples link remains in " + str(path.relative_to(root)))
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = (path.parent / urllib.parse.unquote(target)).resolve()
            if not resolved.exists():
                die("broken local link: " + str(path.relative_to(root)) + " -> " + match.group(1))


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    meta = parse_frontmatter(template)
    validate_metadata(meta)

    main_meta = parse_frontmatter((SRC / "SKILL.md").read_text(encoding="utf-8"))
    main_version = str(main_meta.get("version", "")).strip()
    if main_version != meta["version"]:
        die(
            "version mismatch: template=%s, skills/due-v2/SKILL.md=%s; "
            "bump both before publishing" % (meta["version"], main_version)
        )

    if not REFS.is_dir():
        die("references directory not found: " + str(REFS))

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "references").mkdir(parents=True)

    (OUT / "SKILL.md").write_text(template, encoding="utf-8", newline="\n")

    for source in sorted(REFS.rglob("*")):
        if source.is_dir():
            continue
        if source.suffix.lower() != ".md":
            die("non-Markdown reference file: " + str(source))
        relative = source.relative_to(REFS)
        name = "README.md" if relative.name.upper() == "README.MD" else relative.name
        destination = OUT / "references" / relative.parent / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

    files = sorted(path for path in OUT.rglob("*") if path.is_file())
    total = 0
    for path in files:
        relative = path.relative_to(OUT).as_posix()
        if relative.startswith(".") or "/." in relative:
            die("hidden file: " + relative)
        if path.suffix.lower() not in ALLOWED_EXT:
            die("disallowed file type: " + relative)
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            die("file exceeds 1MB: " + relative)
        total += size
    if len(files) > MAX_FILES:
        die("too many files: %d (limit %d)" % (len(files), MAX_FILES))
    if total > MAX_TOTAL_BYTES:
        die("package exceeds 10MB: %d bytes" % total)
    if not (OUT / "SKILL.md").is_file():
        die("root SKILL.md is missing")

    validate_local_links(OUT)

    version = meta["version"]
    for old in BASE.glob("due-v2-*.zip"):
        old.unlink()
    zip_path = BASE / ("due-v2-" + version + ".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            relative = path.relative_to(OUT).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())

    largest = max(path.stat().st_size for path in files)
    print("SkillHub package: " + str(OUT))
    print("  version: " + version)
    print("  files: %d / %d" % (len(files), MAX_FILES))
    print("  largest: %d bytes / %d" % (largest, MAX_FILE_BYTES))
    print("  total: %d bytes / %d" % (total, MAX_TOTAL_BYTES))
    print("  zip: %s (%d bytes)" % (zip_path, zip_path.stat().st_size))


if __name__ == "__main__":
    main()
