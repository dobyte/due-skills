#!/usr/bin/env python3
"""Read the published version of a SkillHub.cn skill.

It resolves the publisher handle from /api/v1/auth/me (or uses
SKILLHUB_NAMESPACE), then reads /api/v1/skills/<slug>?namespace=<handle> and
prints latestVersion.version.

Exit codes:
  0 - version printed, or skill not found (empty stdout, warning on stderr)
  2 - authentication/network/API error
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_HOST = "https://api.skillhub.cn"
DEFAULT_SLUG = "due-skills"


def fail(message: str) -> None:
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(2)


def get_json(url: str, token: str = "", insecure: bool = False) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(url, headers=headers)
    try:
        context = ssl._create_unverified_context() if insecure else None
        with urllib.request.urlopen(request, timeout=20, context=context) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        fail("network error: " + str(exc.reason))
    try:
        data = json.loads(body) if body else {}
    except json.JSONDecodeError:
        fail("invalid JSON from " + url)
    return status, data if isinstance(data, dict) else {}


def resolve_handle(host: str, token: str, insecure: bool = False) -> str:
    status, data = get_json(host.rstrip("/") + "/api/v1/auth/me", token, insecure)
    if status != 200:
        fail("cannot read /api/v1/auth/me (HTTP %d): %s" % (status, data.get("error") or data))
    user = data.get("user") if isinstance(data.get("user"), dict) else data
    handle = str(user.get("handle") or data.get("handle") or "").strip()
    if not handle:
        fail("the auth response does not contain a handle")
    return handle


def main() -> None:
    parser = argparse.ArgumentParser(description="Read the published SkillHub.cn version")
    parser.add_argument("--host", default=os.environ.get("SKILLHUB_HOST", DEFAULT_HOST))
    parser.add_argument("--slug", default=os.environ.get("SKILLHUB_SLUG", DEFAULT_SLUG))
    parser.add_argument("--namespace", default=os.environ.get("SKILLHUB_NAMESPACE", ""))
    parser.add_argument("--token", default=os.environ.get("SKILLHUB_KEY", ""))
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--allow-anonymous", action="store_true", help="read public skills without a token")
    parser.add_argument("--insecure", action="store_true", help="disable TLS verification for local diagnostics only")
    args = parser.parse_args()

    token = args.token.strip()
    namespace = args.namespace.strip()

    if not token and not args.allow_anonymous:
        fail("SKILLHUB_KEY is required to read the published version")
    if not namespace:
        if not token:
            fail("--namespace is required with --allow-anonymous")
        namespace = resolve_handle(args.host, token, args.insecure)

    detail_url = (
        args.host.rstrip("/")
        + "/api/v1/skills/"
        + urllib.parse.quote(args.slug, safe="")
        + "?"
        + urllib.parse.urlencode({"namespace": namespace})
    )
    status, data = get_json(detail_url, token, args.insecure)

    if status == 404:
        print(
            "WARN: no published skill %s in namespace %s; treating as first release"
            % (args.slug, namespace),
            file=sys.stderr,
        )
        return
    if status != 200:
        fail("cannot read skill detail (HTTP %d): %s" % (status, data.get("error") or data))

    latest = data.get("latestVersion") if isinstance(data.get("latestVersion"), dict) else {}
    version = str(latest.get("version") or data.get("version") or "").strip()
    if not version:
        # A skill exists but has no published version yet.
        print(
            "WARN: skill %s has no published version yet" % args.slug,
            file=sys.stderr,
        )
        return

    if args.json_output:
        print(json.dumps({"slug": args.slug, "namespace": namespace, "version": version}, ensure_ascii=False))
    else:
        print(version)


if __name__ == "__main__":
    main()
