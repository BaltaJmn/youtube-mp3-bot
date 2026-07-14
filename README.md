# 🎵 YouTube → MP3 Bot

Small command-line bot that downloads the audio track of YouTube videos and converts it to MP3 at the best possible quality (LAME VBR ~245 kbps), with the video thumbnail embedded as cover art and ID3 metadata (title, artist) filled in.

Works on **macOS** and **Windows**. Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org).

## Setup (first time only)

### macOS

Requires [Homebrew](https://brew.sh).

```bash
./setup.sh
```

### Windows

Requires [Python](https://www.python.org/downloads/) (check "Add to PATH" during install) and winget (included in Windows 10/11).

```bat
setup.bat
```

The setup script installs `ffmpeg` (audio conversion), `deno` (yt-dlp uses it to solve YouTube's signature challenges — without it downloads fail with `HTTP Error 403: Forbidden`), and `yt-dlp` in a local virtual environment.

## Usage

**Interactive mode** — paste links one at a time:

```bash
./bot.sh          # macOS
bot.bat           # Windows
```

**Direct download** — pass one or more links:

```bash
./bot.sh 'https://www.youtube.com/watch?v=XXXXXXXX'     # macOS
bot.bat "https://www.youtube.com/watch?v=XXXXXXXX"      # Windows
```

MP3 files are saved to the `downloads/` folder.

### Optional: `ytmp3` shortcut (macOS)

Add an alias to your `~/.zshrc` so you can run the bot from anywhere:

```bash
echo 'alias ytmp3="$HOME/path/to/youtube-mp3-bot/bot.sh"' >> ~/.zshrc
```

## Notes

- YouTube serves audio as Opus at ~160 kbps at most; the bot grabs that best-quality track and converts it with LAME's highest-quality setting (`-q 0`, VBR ~245 kbps) so nothing is lost in conversion.
- If downloads stop working someday, update yt-dlp: `./.venv/bin/pip install -U yt-dlp` (YouTube changes often and yt-dlp updates to keep up).

## ☕ Support

If this bot is useful to you and you'd like to support its development:

- [Ko-fi](https://ko-fi.com/baltajmn)

## Disclaimer

This tool is provided for personal and educational use. Downloading content from YouTube may violate [YouTube's Terms of Service](https://www.youtube.com/t/terms). Only download content you have the right to download (your own videos, Creative Commons licensed content, or content whose owner has given you permission). The authors take no responsibility for misuse.

## License

[MIT](LICENSE)
