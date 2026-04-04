#!/bin/bash
# update-feed-metadata.sh
# Run after adding a new episode to feed.xml to update lastBuildDate
# automatically to match the most recent episode's pubDate.
#
# Usage: ./scripts/update-feed-metadata.sh

set -euo pipefail

FEED="$(dirname "$0")/../feed.xml"

if [ ! -f "$FEED" ]; then
    echo "Error: feed.xml not found at $FEED" >&2
    exit 1
fi

# Extract the first (newest) pubDate from the feed
NEWEST_DATE=$(grep -m1 '<pubDate>' "$FEED" | sed 's/.*<pubDate>\(.*\)<\/pubDate>.*/\1/')

if [ -z "$NEWEST_DATE" ]; then
    echo "Error: No pubDate found in feed" >&2
    exit 1
fi

# Update lastBuildDate
sed -i "s|<lastBuildDate>[^<]*</lastBuildDate>|<lastBuildDate>${NEWEST_DATE}</lastBuildDate>|" "$FEED"

echo "Updated lastBuildDate to: $NEWEST_DATE"
