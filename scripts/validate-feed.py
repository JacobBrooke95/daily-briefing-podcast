#!/usr/bin/env python3
"""Validate feed.xml for common issues that break Apple Podcasts sync.

Checks:
  1. XML well-formedness (bare &, unclosed tags, etc.)
  2. Bare ampersands outside CDATA blocks
  3. Required fields on every <item>
  4. itunes:duration format consistency
  5. lastBuildDate matches newest episode
  6. Enclosure files exist on disk (when run from repo root)

Usage:
  python3 scripts/validate-feed.py          # validate feed.xml
  python3 scripts/validate-feed.py feed.xml # explicit path

Exit codes:
  0 = clean
  1 = errors found
"""

import re
import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

FEED_PATH = sys.argv[1] if len(sys.argv) > 1 else "feed.xml"

NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "podcast": "https://podcastindex.org/namespace/1.0",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom": "http://www.w3.org/2005/Atom",
}

errors = []
warnings = []


def error(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


# ── 1. XML well-formedness ──────────────────────────────────────────────

try:
    tree = ET.parse(FEED_PATH)
except ET.ParseError as e:
    error(f"XML parse error: {e}")
    # Can't continue if XML is broken
    print(f"\n{'=' * 60}")
    print(f"FEED VALIDATION: 1 FATAL ERROR")
    print(f"{'=' * 60}")
    for e_msg in errors:
        print(f"  ERROR: {e_msg}")
    print()
    sys.exit(1)

root = tree.getroot()
channel = root.find("channel")
items = channel.findall("item")

# ── 2. Bare ampersands outside CDATA ────────────────────────────────────

with open(FEED_PATH, "r") as f:
    content = f.read()

cdata_ranges = []
for m in re.finditer(r"<!\[CDATA\[.*?\]\]>", content, re.DOTALL):
    cdata_ranges.append((m.start(), m.end()))


def in_cdata(pos):
    for start, end in cdata_ranges:
        if start <= pos < end:
            return True
    return False


lines = content.split("\n")
pos = 0
for line_num, line in enumerate(lines, 1):
    for m in re.finditer(
        r"&(?!amp;|lt;|gt;|apos;|quot;|#\d+;|#x[0-9a-fA-F]+;)", line
    ):
        abs_pos = pos + m.start()
        if not in_cdata(abs_pos):
            ctx = line[max(0, m.start() - 15) : m.start() + 20].strip()
            error(f"Bare '&' outside CDATA at line {line_num}: ...{ctx}...")
    pos += len(line) + 1

# ── 3. Required fields per item ─────────────────────────────────────────

REQUIRED = [
    ("title", None),
    ("guid", None),
    ("pubDate", None),
    ("enclosure", None),
    ("itunes:duration", "itunes"),
    ("itunes:episode", "itunes"),
    ("itunes:episodeType", "itunes"),
]

for i, item in enumerate(items):
    title_el = item.find("title")
    label = title_el.text[:50] if title_el is not None and title_el.text else f"item #{i+1}"

    for tag, ns_key in REQUIRED:
        if ns_key:
            el = item.find(f"{ns_key}:{tag.split(':')[1]}", NS)
        else:
            el = item.find(tag)
        if el is None:
            error(f"[{label}] missing <{tag}>")

    # Check enclosure has required attributes
    enc = item.find("enclosure")
    if enc is not None:
        for attr in ("url", "length", "type"):
            if not enc.get(attr):
                error(f"[{label}] <enclosure> missing '{attr}' attribute")

# ── 4. Duration format ──────────────────────────────────────────────────

DURATION_RE = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")  # M:SS, MM:SS, or HH:MM:SS

for i, item in enumerate(items):
    title_el = item.find("title")
    label = title_el.text[:50] if title_el is not None and title_el.text else f"item #{i+1}"

    dur = item.find("itunes:duration", NS)
    if dur is not None and dur.text:
        if not DURATION_RE.match(dur.text.strip()):
            warn(f"[{label}] non-standard duration format: '{dur.text}' (use MM:SS or HH:MM:SS)")

# ── 5. lastBuildDate freshness ──────────────────────────────────────────

build_date_el = channel.find("lastBuildDate")
if build_date_el is not None and items:
    first_item_pub = items[0].find("pubDate")
    if first_item_pub is not None:
        try:
            build_dt = parsedate_to_datetime(build_date_el.text)
            newest_dt = parsedate_to_datetime(first_item_pub.text)
            if build_dt < newest_dt:
                warn(
                    f"lastBuildDate ({build_date_el.text.strip()}) is older than "
                    f"newest episode ({first_item_pub.text.strip()}). "
                    f"Run ./scripts/update-feed-metadata.sh"
                )
        except Exception:
            pass

# ── 6. Enclosure files exist on disk ────────────────────────────────────

repo_root = os.path.dirname(os.path.dirname(os.path.abspath(FEED_PATH)))
episodes_dir = os.path.join(repo_root, "episodes")

if os.path.isdir(episodes_dir):
    for i, item in enumerate(items):
        title_el = item.find("title")
        label = title_el.text[:50] if title_el is not None and title_el.text else f"item #{i+1}"

        enc = item.find("enclosure")
        if enc is not None:
            url = enc.get("url", "")
            filename = url.split("/")[-1]
            local_path = os.path.join(episodes_dir, filename)
            if filename and not os.path.exists(local_path):
                warn(f"[{label}] audio file not found: episodes/{filename}")

# ── Report ──────────────────────────────────────────────────────────────

print(f"\nFeed: {FEED_PATH}  ({len(items)} episodes)")
print(f"{'=' * 60}")

if not errors and not warnings:
    print("ALL CHECKS PASSED")
    print(f"{'=' * 60}\n")
    sys.exit(0)

if errors:
    print(f"\nERRORS ({len(errors)}):")
    for msg in errors:
        print(f"  x {msg}")

if warnings:
    print(f"\nWARNINGS ({len(warnings)}):")
    for msg in warnings:
        print(f"  ! {msg}")

print(f"\n{'=' * 60}\n")
sys.exit(1 if errors else 0)
