#!/usr/bin/env python3
"""Web front-end for the bot, to get MP3s straight onto a phone.

Paste a YouTube link: the download runs in the background through bot.sh
(which updates yt-dlp and retries on failure) and the MP3 shows up in the list.
The server is only a relay: an MP3 is deleted an hour after the phone
downloads it, and whatever is never picked up goes after a day.

    ./.venv/bin/python web.py    # http://127.0.0.1:8765

It has no login of its own: it only listens on localhost, and whatever exposes
it must authenticate first (Cloudflare Access on the Raspberry Pi).
"""

import html
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bot import DOWNLOADS_DIR

BOT_SH = Path(__file__).resolve().parent / "bot.sh"
PORT = 8765
MAX_AGE = 24 * 3600  # seconds an MP3 waits to be picked up
GRACE = 3600  # seconds an MP3 stays after being downloaded, for a retry

jobs = {}  # link -> "downloading" | "failed"
# ponytail: one download at a time, the Pi 3 has 1 GB of RAM; a pool if it ever needs more
one_at_a_time = threading.Lock()

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{refresh}<title>YouTube MP3</title>
<style>
body {{ font: 16px system-ui, sans-serif; max-width: 40rem; margin: 1rem auto; padding: 0 1rem; }}
form {{ display: flex; gap: .5rem; }}
input {{ flex: 1; min-width: 0; font: inherit; padding: .6rem; }}
button {{ font: inherit; padding: .6rem 1rem; }}
li, p {{ margin: .6rem 0; overflow-wrap: anywhere; }}
small {{ color: #888; }}
@media (prefers-color-scheme: dark) {{ body {{ background: #111; color: #eee; }} a {{ color: #8ab4f8; }} }}
</style></head><body>
<h1>YouTube MP3</h1>
<form method="post"><input name="link" type="url" placeholder="YouTube link" required><button>Download</button></form>
{jobs}
<ul>{files}</ul>
<p><small>Each MP3 is deleted from the server an hour after it is downloaded, or after 24 h if it never is.</small></p>
</body></html>"""


def is_youtube_video(link: str) -> bool:
    """Only single YouTube videos reach yt-dlp: it would fetch almost any URL
    otherwise, and a playlist or channel link would download all of it.

    >>> is_youtube_video("https://www.youtube.com/watch?v=abc")
    True
    >>> is_youtube_video("https://www.youtube.com/watch?v=abc&list=RDabc")
    True
    >>> is_youtube_video("https://youtu.be/abc?si=xyz")
    True
    >>> is_youtube_video("https://music.youtube.com/watch?v=abc")
    True
    >>> is_youtube_video("https://m.youtube.com/shorts/abc")
    True
    >>> is_youtube_video("https://www.youtube.com/live/abc")
    True
    >>> is_youtube_video("https://www.youtube.com/playlist?list=PLabc")
    False
    >>> is_youtube_video("https://www.youtube.com/@channel/videos")
    False
    >>> is_youtube_video("https://youtu.be/")
    False
    >>> is_youtube_video("https://youtube.com.evil.net/watch?v=abc")
    False
    >>> is_youtube_video("https://youtube.com@evil.net/watch?v=abc")
    False
    >>> is_youtube_video("http://192.168.1.1/")
    False
    >>> is_youtube_video("ytsearch:some song")
    False
    """
    url = urllib.parse.urlsplit(link)
    host = (url.hostname or "").lower()
    if url.scheme not in ("http", "https"):
        return False
    if host == "youtu.be":
        return len(url.path) > 1
    if host == "youtube.com" or host.endswith(".youtube.com"):
        # A watch link that also names a playlist is fine: bot.py sets noplaylist
        watch = url.path == "/watch" and "v" in urllib.parse.parse_qs(url.query)
        return watch or url.path.startswith(("/shorts/", "/live/"))
    return False


def run(link: str) -> None:
    ok = False
    with one_at_a_time:
        # yt-dlp writes the MP3 long before it is finished: convert out of sight
        # and only move it to the list once it is complete.
        work = Path(tempfile.mkdtemp(prefix=".job-", dir=DOWNLOADS_DIR))
        try:
            env = {**os.environ, "MP3_DOWNLOADS_DIR": str(work)}
            ok = subprocess.run([str(BOT_SH), link], env=env).returncode == 0
            if ok:
                for mp3 in work.glob("*.mp3"):
                    ready = mp3.replace(DOWNLOADS_DIR / mp3.name)
                    ready.touch()  # yt-dlp may date it to the upload; MAX_AGE counts from now
        finally:
            shutil.rmtree(work, ignore_errors=True)
            if ok:
                jobs.pop(link, None)
            else:
                jobs[link] = "failed"


def render() -> str:
    current = list(jobs.items())
    job_lines = "".join(
        f"<p>{'⏳ Downloading' if state == 'downloading' else '❌ Failed'}: "
        f"{html.escape(link)}</p>"
        for link, state in current
    )
    mp3s = []
    for p in DOWNLOADS_DIR.glob("*.mp3"):
        try:
            st = p.stat()
        except FileNotFoundError:  # the phone finished picking it up meanwhile
            continue
        if st.st_mtime < time.time() - MAX_AGE:
            p.unlink(missing_ok=True)
        else:
            mp3s.append((st.st_mtime, p, st.st_size))
    file_lines = "".join(
        f'<li><a href="/{urllib.parse.quote(p.name)}" download>{html.escape(p.stem)}</a> '
        f"<small>{size / 1e6:.0f} MB</small></li>"
        for _, p, size in sorted(mp3s, reverse=True)
    )
    downloading = any(state == "downloading" for _, state in current)
    # Reload to show progress, but never over a link that is being pasted
    refresh = (
        "<script>setInterval(() => document.querySelector('input').value || location.reload(), 10000)</script>\n"
        if downloading
        else ""
    )
    return PAGE.format(refresh=refresh, jobs=job_lines, files=file_lines)


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urllib.parse.urlsplit(self.path).path != "/":
            return super().do_GET()  # serves the MP3s from DOWNLOADS_DIR
        body = render().encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def copyfile(self, source, outputfile):
        super().copyfile(source, outputfile)
        # Only reached once the whole file left the Pi (a dropped connection
        # raises), but Cloudflare may still be relaying the tail to a phone on
        # flaky data: keep it a while so a failed download can be retried.
        delete = threading.Timer(GRACE, Path(source.name).unlink, kwargs={"missing_ok": True})
        delete.daemon = True
        delete.start()

    def list_directory(self, path):
        self.send_error(404)

    def do_POST(self):
        length = min(int(self.headers.get("Content-Length") or 0), 4096)
        form = urllib.parse.parse_qs(self.rfile.read(length).decode(errors="replace"))
        link = form.get("link", [""])[0].strip()
        if not is_youtube_video(link):
            return self.send_error(400, "Not a link to a single YouTube video")
        if jobs.get(link) != "downloading":
            jobs[link] = "downloading"
            threading.Thread(target=run, args=(link,), daemon=True).start()
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


def main() -> None:
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    for leftover in DOWNLOADS_DIR.glob(".job-*"):  # jobs cut short by a restart
        shutil.rmtree(leftover, ignore_errors=True)
    handler = partial(Handler, directory=str(DOWNLOADS_DIR))
    print(f"Listening on http://127.0.0.1:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), handler).serve_forever()


if __name__ == "__main__":
    main()
