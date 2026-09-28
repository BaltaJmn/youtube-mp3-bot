#!/usr/bin/env python3
"""Bot that downloads the audio of YouTube videos as MP3 (best quality).

Usage:
    python3 bot.py                  # interactive mode: paste links one by one
    python3 bot.py <link> [<link>]  # direct download of one or more links
    python3 bot.py --m4a ...        # fast mode: YouTube's own AAC audio, no conversion
"""

import os
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit(
        "yt-dlp is missing. Run the setup script first, or install it with: pip3 install yt-dlp"
    )

# web.py points this at a private folder per job, so half-converted files never show up
DOWNLOADS_DIR = Path(
    os.environ.get("MP3_DOWNLOADS_DIR") or Path(__file__).resolve().parent / "downloads"
)


def download_options(m4a: bool = False) -> dict:
    if m4a:
        # YouTube already serves AAC (~130 kbps) in .m4a: it is copied as is,
        # so a 2-hour set takes seconds instead of minutes. Plays on any phone.
        fmt = "bestaudio[ext=m4a]/bestaudio/best"
        audio = {"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}
    else:
        # Best audio track available (usually Opus ~160 kbps on YouTube)
        fmt = "bestaudio/best"
        audio = {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            # "0" = best VBR quality the LAME encoder offers (~245 kbps)
            "preferredquality": "0",
        }
    return {
        "format": fmt,
        "outtmpl": str(DOWNLOADS_DIR / "%(title)s.%(ext)s"),
        "postprocessors": [
            audio,
            # Adds title, artist, etc. as tags
            {"key": "FFmpegMetadata"},
            # Embeds the video thumbnail as cover art
            {"key": "EmbedThumbnail"},
        ],
        "writethumbnail": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }


def download(link: str, m4a: bool = False) -> bool:
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(download_options(m4a)) as ydl:
            info = ydl.extract_info(link, download=True)
        title = info.get("title", "unknown")
        print(f"\n✅ Downloaded: {title}")
        print(f"   Saved to: {DOWNLOADS_DIR}\n")
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Failed to download {link}: {e}\n")
        return False


def interactive_mode(m4a: bool) -> None:
    print("🎵 YouTube → MP3 download bot" + (" (fast mode: m4a)" if m4a else ""))
    print(f"   Files are saved to: {DOWNLOADS_DIR}")
    print("   Paste a YouTube link and press Enter ('quit' to exit).\n")
    while True:
        try:
            link = input("Link > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not link:
            continue
        if link.lower() in {"quit", "exit", "q"}:
            print("Bye!")
            break
        download(link, m4a)


def main() -> None:
    m4a = "--m4a" in sys.argv[1:]
    links = [arg for arg in sys.argv[1:] if arg != "--m4a"]
    if links:
        failures = sum(not download(link, m4a) for link in links)
        sys.exit(1 if failures else 0)
    interactive_mode(m4a)


if __name__ == "__main__":
    main()
