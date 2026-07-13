#!/usr/bin/env python3
"""Bot that downloads the audio of YouTube videos as MP3 (best quality).

Usage:
    python3 bot.py                  # interactive mode: paste links one by one
    python3 bot.py <link> [<link>]  # direct download of one or more links
"""

import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    sys.exit(
        "yt-dlp is missing. Run the setup script first, or install it with: pip3 install yt-dlp"
    )

DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"


def download_options() -> dict:
    return {
        # Best audio track available (usually Opus ~160 kbps on YouTube)
        "format": "bestaudio/best",
        "outtmpl": str(DOWNLOADS_DIR / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                # "0" = best VBR quality the LAME encoder offers (~245 kbps)
                "preferredquality": "0",
            },
            # Adds title, artist, etc. as ID3 tags
            {"key": "FFmpegMetadata"},
            # Embeds the video thumbnail as MP3 cover art
            {"key": "EmbedThumbnail"},
        ],
        "writethumbnail": True,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": True,
    }


def download(link: str) -> bool:
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    try:
        with yt_dlp.YoutubeDL(download_options()) as ydl:
            info = ydl.extract_info(link, download=True)
        title = info.get("title", "unknown")
        print(f"\n✅ Downloaded: {title}")
        print(f"   Saved to: {DOWNLOADS_DIR}\n")
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Failed to download {link}: {e}\n")
        return False


def interactive_mode() -> None:
    print("🎵 YouTube → MP3 download bot")
    print(f"   MP3 files are saved to: {DOWNLOADS_DIR}")
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
        download(link)


def main() -> None:
    links = sys.argv[1:]
    if links:
        failures = sum(not download(link) for link in links)
        sys.exit(1 if failures else 0)
    interactive_mode()


if __name__ == "__main__":
    main()
