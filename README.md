# 🎵 YouTube → MP3 Bot

Small command-line bot that downloads the audio track of YouTube videos and converts it to MP3 at the best possible quality (LAME VBR ~245 kbps), with the video thumbnail embedded as cover art and ID3 metadata (title, artist) filled in.

Works on **macOS**, **Windows** and **Linux** (Debian, Raspberry Pi OS), and can run on a Raspberry Pi as a small web page for your phone. Built on [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://ffmpeg.org).

## Setup (first time only)

### macOS and Linux

On macOS it requires [Homebrew](https://brew.sh); on Linux it uses `apt`.

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

**Fast mode**: add `--m4a` to skip the MP3 conversion and keep YouTube's own AAC audio (~130 kbps) in an `.m4a` file. It plays on any phone, and a 2-hour set is ready in seconds instead of minutes:

```bash
./bot.sh --m4a 'https://www.youtube.com/watch?v=XXXXXXXX'
```

### Optional: `ytmp3` shortcut (macOS)

Add an alias to your `~/.zshrc` so you can run the bot from anywhere:

```bash
echo 'alias ytmp3="$HOME/path/to/youtube-mp3-bot/bot.sh"' >> ~/.zshrc
```

### Optional: from your phone, anywhere (Raspberry Pi)

`web.py` is a one-page front-end: paste a link on your phone, the server downloads it in fast mode (`.m4a`, no conversion) and a link to the file shows up when it is ready. Files stay on the server as a library, to download again from any device, until you delete them from the page. Only links to a single video are accepted, never playlists or channels.

On a Raspberry Pi with a 64-bit OS (Deno has no 32-bit ARM build):

```bash
./setup.sh                                   # apt installs ffmpeg, Deno goes to /usr/local
sudo cp mp3-web.service /etc/systemd/system/ # assumes the repo is in /home/pi/youtube-mp3-bot
sudo systemctl enable --now mp3-web          # listens on 127.0.0.1:8765 only
```

To keep yt-dlp current without waiting for a download to fail, update it every night (`crontab -e`):

```
17 5 * * * $HOME/youtube-mp3-bot/.venv/bin/pip install --upgrade --quiet "yt-dlp[default]" 2>&1 | logger -t yt-dlp-update
```

Each download runs in its own process, so the new version is picked up without restarting `mp3-web`.

`web.py` has no login of its own, so never publish the port directly. To reach it from outside home, put a [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) in front of `http://127.0.0.1:8765` and a [Cloudflare Access](https://developers.cloudflare.com/cloudflare-one/applications/) application on the same hostname, allowing only your email.

## Notes

- YouTube serves audio as Opus at ~160 kbps at most; the bot grabs that best-quality track and converts it with LAME's highest-quality setting (`-q 0`, VBR ~245 kbps) so nothing is lost in conversion.
- YouTube changes often and breaks old yt-dlp versions. When a download fails, `bot.sh` and `bot.bat` update yt-dlp and retry on their own; to update by hand: `./.venv/bin/pip install -U "yt-dlp[default]"`.

## ☕ Support

If this bot is useful to you and you'd like to support its development:

- [Ko-fi](https://ko-fi.com/baltajmn)

## Disclaimer

This tool is provided for personal and educational use. Downloading content from YouTube may violate [YouTube's Terms of Service](https://www.youtube.com/t/terms). Only download content you have the right to download (your own videos, Creative Commons licensed content, or content whose owner has given you permission). The authors take no responsibility for misuse.

## License

[MIT](LICENSE)
