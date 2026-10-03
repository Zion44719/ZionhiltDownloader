# Quantify Media Downloader

> Download audio and video from anywhere. Fast, clean, no fuss.

Quantify is a lightweight Python desktop app that lets you paste any media URL and pull it down as a video file or extracted audio — with live progress, quality control, and a folder picker, all in one window.

---

## Features

- **Video download** — saves as MP4 at your chosen quality (Best, 1080p, 720p, 480p, 360p)
- **Audio extraction** — saves as MP3 at your chosen bitrate (Best, 320k, 192k, 128k, 64k)
- **Live progress bar** — shows percentage, download speed, and ETA in real time
- **Folder picker** — choose exactly where files land
- **Cancel mid-download** — stop any download cleanly
- **1000+ supported sites** — YouTube, Twitter/X, Vimeo, SoundCloud, Reddit, and [many more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) *(required for 1080p video merging and audio extraction)*

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/quantify.git
cd quantify
```

**2. Install Python dependency**

```bash
pip install yt-dlp
```

**3. Install ffmpeg**

| Platform | Command |
|----------|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Windows | Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH |

---

## Usage

```bash
python downloader.py
```

1. Paste a URL into the input field
2. Choose **video** or **audio** from the Format dropdown
3. Pick a quality level
4. (Optional) click **Browse** to change the save folder
5. Click **Download**

Files are saved to `~/Downloads` by default.

---

## Project Structure

```
quantify/
├── downloader.py   # Main application
└── README.md       # This file
```

---


## Supported Sites

https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

---
## Tech Stack

| Component | Library |
|-----------|---------|
| GUI | `tkinter` (stdlib) |
| Downloading | `yt-dlp` |
| Media processing | `ffmpeg` (external) |

---

## License

MIT — do whatever you want with it.
