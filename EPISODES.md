# Publishing New Episodes

Step-by-step guide for adding episodes to Jacob's Daily Briefing podcast feed.

## Directory Structure

```
daily-briefing-podcast/
├── feed.xml                  # RSS feed (edit this to add episodes)
├── podcast-cover.jpg         # Channel artwork (3000x3000 JPEG)
├── episodes/                 # Audio files (.mp3 or .m4a)
├── artwork/                  # Episode artwork (.jpg, 1400-3000px square)
├── transcripts/              # WebVTT transcript files (.vtt)
└── scripts/
    └── update-feed-metadata.sh   # Updates lastBuildDate automatically
```

## File Naming Conventions

| Type | Pattern | Examples |
|------|---------|---------|
| Audio | `briefing-YYYY-MM-DD.mp3` | `briefing-2026-04-04.mp3` |
| Audio (deep dive) | `TOPIC-deepdive-YYYY-MM-DD.mp3` | `cabin-deepdive-2026-04-01.mp3` |
| Audio (series) | `SERIES-chNN-YYYY-MM-DD.mp3` | `keeping-house-ch05-2026-04-03.mp3` |
| Artwork | `episode-art-YYYY-MM-DD.jpg` | `episode-art-2026-04-04.jpg` |
| Artwork (special) | `episode-art-YYYY-MM-DD-TOPIC.jpg` | `episode-art-2026-04-01-cabin.jpg` |
| Transcript | `transcript-YYYY-MM-DD.vtt` | `transcript-2026-04-04.vtt` |
| Transcript (special) | `transcript-YYYY-MM-DD-TOPIC.vtt` | `transcript-2026-04-03-keeping-house-ch05.vtt` |

## Step-by-Step: Adding a New Episode

### 1. Prepare your files

Place each file in the correct directory:

```bash
cp my-episode.mp3    episodes/briefing-2026-04-05.mp3
cp my-artwork.jpg    artwork/episode-art-2026-04-05.jpg
cp my-transcript.vtt transcripts/transcript-2026-04-05.vtt
```

### 2. Get the audio file size in bytes

The `<enclosure>` tag requires the exact file size. Get it with:

```bash
wc -c < episodes/briefing-2026-04-05.mp3
```

### 3. Get the episode duration

```bash
ffprobe -i episodes/briefing-2026-04-05.mp3 -show_entries format=duration \
  -v quiet -of csv="p=0" | python3 -c "
import sys; s=float(sys.stdin.read())
print(f'{int(s//60)}:{int(s%60):02d}')"
```

Or note the duration from your audio editor. Format: `M:SS` or `MM:SS`.

### 4. Determine the next episode number

Check the current highest episode number in `feed.xml`:

```bash
grep -m1 '<itunes:episode>' feed.xml
```

Your new episode number = that number + 1.

### 5. Add the `<item>` block to feed.xml

Open `feed.xml` and insert a new `<item>` block **directly after** the `<podcast:txt>` channel tag and blank line (before the first existing `<item>`). New episodes always go at the top.

#### Template: Daily Briefing

```xml
    <item>
      <title>Daily Briefing — DAY, MONTH DD, YYYY</title>
      <description>Morning daily briefing for DAY, MONTH DD, YYYY. SUMMARY.

      00:00:00 Opening &amp; Weather
      00:00:30 Calendar &amp; Schedule
      00:01:00 Messages
      00:01:30 Top Stories
      00:03:00 Tech &amp; AI
      00:04:00 Local News
      00:04:30 Closing</description>
      <content:encoded><![CDATA[
      <h2>Story Headline</h2>
      <p>Story summary. <a href="https://example.com">Read more →</a></p>
      ]]></content:encoded>
      <enclosure url="https://jacobbrooke95.github.io/daily-briefing-podcast/episodes/FILENAME.mp3" length="FILE_SIZE_BYTES" type="audio/mpeg"/>
      <itunes:image href="https://jacobbrooke95.github.io/daily-briefing-podcast/artwork/ARTWORK_FILENAME.jpg"/>
      <podcast:transcript url="https://jacobbrooke95.github.io/daily-briefing-podcast/transcripts/TRANSCRIPT_FILENAME.vtt" type="text/vtt" language="en"/>
      <guid isPermaLink="false">briefing-YYYY-MM-DD</guid>
      <pubDate>DAY, DD MON YYYY HH:MM:SS -0500</pubDate>
      <itunes:duration>M:SS</itunes:duration>
      <itunes:episode>EPISODE_NUMBER</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>
```

#### Template: Deep Dive

```xml
    <item>
      <title>TOPIC — Deep Dive</title>
      <description>DETAILED_DESCRIPTION.

      00:00:00 Introduction
      00:02:00 Section One
      00:10:00 Section Two
      00:20:00 Conclusion</description>
      <content:encoded><![CDATA[<h2>Title</h2>
      <p>Summary with links.</p>]]></content:encoded>
      <enclosure url="https://jacobbrooke95.github.io/daily-briefing-podcast/episodes/FILENAME.mp3" length="FILE_SIZE_BYTES" type="audio/mpeg"/>
      <itunes:image href="https://jacobbrooke95.github.io/daily-briefing-podcast/artwork/ARTWORK_FILENAME.jpg"/>
      <podcast:transcript url="https://jacobbrooke95.github.io/daily-briefing-podcast/transcripts/TRANSCRIPT_FILENAME.vtt" type="text/vtt" language="en"/>
      <guid isPermaLink="false">deepdive-YYYY-MM-DD-TOPIC</guid>
      <pubDate>DAY, DD MON YYYY HH:MM:SS -0500</pubDate>
      <itunes:duration>MM:SS</itunes:duration>
      <itunes:episode>EPISODE_NUMBER</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>
```

#### Template: Series Chapter (e.g., The Keeping House)

```xml
    <item>
      <title>Chapter N — CHAPTER_TITLE (SERIES_NAME)</title>
      <description>Chapter N of SERIES_NAME. DESCRIPTION.

      00:00:00 Opening
      00:01:00 Scene One
      00:10:00 Scene Two</description>
      <content:encoded><![CDATA[<h2>Chapter N — CHAPTER_TITLE</h2>
      <p><strong>POV:</strong> Character | <strong>Season:</strong> Theme</p>
      <p>Chapter summary.</p>
      <p><em>SERIES_NAME</em> is an original literary novel published chapter by chapter.</p>]]></content:encoded>
      <enclosure url="https://jacobbrooke95.github.io/daily-briefing-podcast/episodes/FILENAME.mp3" length="FILE_SIZE_BYTES" type="audio/mpeg"/>
      <itunes:image href="https://jacobbrooke95.github.io/daily-briefing-podcast/artwork/ARTWORK_FILENAME.jpg"/>
      <podcast:transcript url="https://jacobbrooke95.github.io/daily-briefing-podcast/transcripts/TRANSCRIPT_FILENAME.vtt" type="text/vtt" language="en"/>
      <guid isPermaLink="false">deepdive-YYYY-MM-DD-SERIES-chNN</guid>
      <pubDate>DAY, DD MON YYYY HH:MM:SS -0500</pubDate>
      <itunes:duration>MM:SS</itunes:duration>
      <itunes:episode>EPISODE_NUMBER</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>
```

### 6. Update the lastBuildDate

```bash
./scripts/update-feed-metadata.sh
```

This automatically sets `<lastBuildDate>` to the newest episode's `<pubDate>`.

### 7. Validate the feed

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('feed.xml'); print('Valid XML')"
```

### 8. Commit and push

```bash
git add episodes/FILENAME.mp3 artwork/ARTWORK.jpg transcripts/TRANSCRIPT.vtt feed.xml
git commit -m "Daily Briefing — DAY, MONTH DD, YYYY"
git push origin main
```

The site updates automatically via GitHub Pages once pushed.

## Field Reference

### Required per episode

| Field | Description |
|-------|-------------|
| `<title>` | Episode title |
| `<description>` | Plain-text summary with chapter timestamps |
| `<content:encoded>` | Rich HTML show notes (wrap in `<![CDATA[...]]>` or escape HTML entities) |
| `<enclosure>` | Audio URL, exact byte length, MIME type (`audio/mpeg` for MP3, `audio/mp4` for M4A) |
| `<itunes:image>` | Episode artwork URL (1400-3000px square JPEG) |
| `<podcast:transcript>` | Transcript URL, type `text/vtt`, language `en` |
| `<guid>` | Unique ID with `isPermaLink="false"` — never reuse or change after publishing |
| `<pubDate>` | RFC 2822 date (e.g., `Sat, 04 Apr 2026 06:13:07 -0500`) |
| `<itunes:duration>` | Length in `M:SS` or `MM:SS` format |
| `<itunes:episode>` | Sequential episode number (integer) |
| `<itunes:episodeType>` | `full`, `trailer`, or `bonus` |
| `<itunes:explicit>` | `true` or `false` |

### Episode artwork requirements

- **Dimensions:** 1400x1400 to 3000x3000 pixels (square)
- **Format:** JPEG (.jpg) only (PNG also accepted but JPEG preferred)
- **Color space:** RGB (not CMYK)
- **File size:** Under 500 KB recommended
- **File name:** Must end in `.jpg` or `.png`

### Transcript format (WebVTT)

```
WEBVTT

00:00:00.000 --> 00:00:05.000
Good morning, here's your daily briefing.

00:00:05.000 --> 00:00:12.000
First up, the latest on...
```

### Chapter timestamps in description

Include chapter markers in the `<description>` field using `HH:MM:SS` format. Podcast apps parse these automatically:

```
00:00:00 Opening & Weather
00:00:28 Calendar & Schedule
00:01:15 Top Stories
```

Use `&amp;` for ampersands in the description (it's XML).

## Supported RSS Tags (Full Reference)

### Channel-level tags (in feed.xml header)

| Tag | Current Value | Purpose |
|-----|---------------|---------|
| `<title>` | Jacob's Daily Briefing | Show name |
| `<link>` | GitHub Pages URL | Show website |
| `<atom:link rel="self">` | feed.xml URL | Feed self-reference |
| `<description>` | Show summary | Directory listing |
| `<language>` | en-us | Language code |
| `<itunes:author>` | Jacob Brooke | Creator name |
| `<itunes:owner>` | Name + email | Apple Podcasts contact |
| `<itunes:image>` | podcast-cover.jpg | Show artwork (primary) |
| `<image>` | podcast-cover.jpg | Show artwork (RSS fallback) |
| `<itunes:category>` | News > Daily News | Apple category |
| `<itunes:explicit>` | false | Content rating |
| `<itunes:type>` | episodic | Newest-first ordering |
| `<copyright>` | 2026 Jacob Brooke | Rights statement |
| `<lastBuildDate>` | Auto-updated | Feed freshness signal |
| `<podcast:guid>` | UUID v5 | Cross-platform podcast identity |
| `<podcast:medium>` | podcast | Content type declaration |
| `<podcast:locked>` | no | Import control |
| `<podcast:txt>` | AI disclosure | Machine-readable AI content flag |

## Troubleshooting

**Apple Podcasts not updating artwork?**
Change the artwork filename and URL — Apple caches aggressively and may not refresh if the URL stays the same.

**Feed not loading?**
Validate XML first. A single unescaped `&` or unclosed tag breaks the entire feed. Common fixes:
- Use `&amp;` instead of `&` in descriptions
- Wrap HTML content in `<![CDATA[...]]>` or escape all entities
- Ensure the XML declaration is on line 1 with no whitespace before it

**Enclosure length wrong?**
Apple Podcasts may reject or misreport episodes with incorrect file sizes. Always use `wc -c < file.mp3` to get the exact byte count.

**Episode not appearing?**
- Check that `<pubDate>` is not in the future
- Verify `<guid>` is unique across all episodes
- Ensure the `<item>` is inside the `<channel>` block
