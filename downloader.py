import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys

try:
    import yt_dlp
except ImportError:
    messagebox.showerror("Missing dependency", "Please run: pip install yt-dlp")
    sys.exit(1)


# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#0F0F13"
PANEL     = "#1A1A22"
BORDER    = "#2A2A38"
ACCENT    = "#7C5CFC"        # violet
ACCENT2   = "#B490FF"        # lighter violet for hover
TEXT      = "#E8E8F0"
SUBTEXT   = "#8888AA"
SUCCESS   = "#4ECDC4"
ERROR     = "#FF6B6B"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10) if sys.platform == "win32" else ("Helvetica", 10)
FONT_BIG  = ("Segoe UI", 22, "bold") if sys.platform == "win32" else ("Helvetica", 22, "bold")
FONT_LBL  = ("Segoe UI", 9) if sys.platform == "win32" else ("Helvetica", 9)


class DownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Media Downloader")
        self.geometry("700x560")
        self.minsize(600, 480)
        self.configure(bg=BG)
        self.resizable(True, True)

        self._save_dir = os.path.expanduser("~/Downloads")
        self._cancel   = threading.Event()
        self._thread   = None

        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=BG, pady=20)
        hdr.pack(fill="x", padx=30)

        tk.Label(hdr, text="⬇  Media Downloader", font=FONT_BIG,
                 bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(hdr, text="Paste a link · choose format · download",
                 font=FONT_LBL, bg=BG, fg=SUBTEXT).pack(anchor="w", pady=(2, 0))

        # ── Divider ──
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=30)

        # ── Main card ──
        card = tk.Frame(self, bg=PANEL, bd=0)
        card.pack(fill="both", expand=True, padx=30, pady=20)

        inner = tk.Frame(card, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        # URL row
        tk.Label(inner, text="URL", font=FONT_LBL, bg=PANEL, fg=SUBTEXT).pack(anchor="w")
        url_frame = tk.Frame(inner, bg=BORDER, padx=1, pady=1)
        url_frame.pack(fill="x", pady=(4, 16))

        url_inner = tk.Frame(url_frame, bg=PANEL)
        url_inner.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(
            url_inner, textvariable=self.url_var,
            font=FONT_UI, bg=PANEL, fg=TEXT,
            insertbackground=ACCENT, relief="flat",
            bd=8
        )
        self.url_entry.pack(side="left", fill="x", expand=True)

        self._btn_clear = tk.Button(
            url_inner, text="✕", font=FONT_LBL,
            bg=PANEL, fg=SUBTEXT, relief="flat",
            activebackground=PANEL, activeforeground=ERROR,
            cursor="hand2", command=self._clear_url, padx=8
        )
        self._btn_clear.pack(side="right")

        # Format + Quality row
        opt_row = tk.Frame(inner, bg=PANEL)
        opt_row.pack(fill="x", pady=(0, 16))

        # Format
        fmt_col = tk.Frame(opt_row, bg=PANEL)
        fmt_col.pack(side="left", fill="x", expand=True, padx=(0, 12))
        tk.Label(fmt_col, text="FORMAT", font=FONT_LBL, bg=PANEL, fg=SUBTEXT).pack(anchor="w")

        self.fmt_var = tk.StringVar(value="video")
        fmt_frame = tk.Frame(fmt_col, bg=BORDER, padx=1, pady=1)
        fmt_frame.pack(fill="x", pady=(4, 0))
        self.fmt_menu = ttk.Combobox(
            fmt_frame, textvariable=self.fmt_var,
            values=["video", "audio"],
            state="readonly", font=FONT_UI
        )
        self.fmt_menu.pack(fill="x")
        self.fmt_var.trace_add("write", self._on_format_change)

        # Quality
        qual_col = tk.Frame(opt_row, bg=PANEL)
        qual_col.pack(side="left", fill="x", expand=True)
        tk.Label(qual_col, text="QUALITY", font=FONT_LBL, bg=PANEL, fg=SUBTEXT).pack(anchor="w")

        self.qual_var = tk.StringVar(value="best")
        qual_frame = tk.Frame(qual_col, bg=BORDER, padx=1, pady=1)
        qual_frame.pack(fill="x", pady=(4, 0))
        self.qual_menu = ttk.Combobox(
            qual_frame, textvariable=self.qual_var,
            values=["best", "1080p", "720p", "480p", "360p"],
            state="readonly", font=FONT_UI
        )
        self.qual_menu.pack(fill="x")

        # Save folder row
        tk.Label(inner, text="SAVE TO", font=FONT_LBL, bg=PANEL, fg=SUBTEXT).pack(anchor="w")
        dir_frame = tk.Frame(inner, bg=BORDER, padx=1, pady=1)
        dir_frame.pack(fill="x", pady=(4, 16))

        dir_inner = tk.Frame(dir_frame, bg=PANEL)
        dir_inner.pack(fill="x")

        self.dir_label = tk.Label(
            dir_inner, text=self._save_dir,
            font=FONT_UI, bg=PANEL, fg=TEXT,
            anchor="w", padx=8, pady=6
        )
        self.dir_label.pack(side="left", fill="x", expand=True)

        tk.Button(
            dir_inner, text="Browse", font=FONT_LBL,
            bg=ACCENT, fg="#FFFFFF", relief="flat",
            activebackground=ACCENT2, cursor="hand2",
            padx=12, pady=4, command=self._browse
        ).pack(side="right", padx=4, pady=4)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Violet.Horizontal.TProgressbar",
                        troughcolor=BORDER,
                        background=ACCENT,
                        bordercolor=PANEL,
                        lightcolor=ACCENT,
                        darkcolor=ACCENT)
        self.progress = ttk.Progressbar(
            inner, variable=self.progress_var,
            style="Violet.Horizontal.TProgressbar",
            mode="determinate", maximum=100
        )
        self.progress.pack(fill="x", pady=(0, 8))

        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.status_lbl = tk.Label(
            inner, textvariable=self.status_var,
            font=FONT_MONO, bg=PANEL, fg=SUBTEXT,
            anchor="w", wraplength=600
        )
        self.status_lbl.pack(anchor="w", pady=(0, 16))

        # Buttons row
        btn_row = tk.Frame(inner, bg=PANEL)
        btn_row.pack(fill="x")

        self.dl_btn = tk.Button(
            btn_row, text="Download",
            font=(FONT_UI[0], 11, "bold"),
            bg=ACCENT, fg="#FFFFFF", relief="flat",
            activebackground=ACCENT2, cursor="hand2",
            padx=24, pady=10, command=self._start_download
        )
        self.dl_btn.pack(side="left")

        self.cancel_btn = tk.Button(
            btn_row, text="Cancel",
            font=FONT_UI, bg=BORDER, fg=SUBTEXT,
            relief="flat", activebackground=BORDER,
            cursor="hand2", padx=18, pady=10,
            command=self._cancel_download, state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=(10, 0))

        self.open_btn = tk.Button(
            btn_row, text="Open folder",
            font=FONT_UI, bg=PANEL, fg=SUBTEXT,
            relief="flat", activebackground=PANEL,
            cursor="hand2", padx=18, pady=10,
            command=self._open_folder
        )
        self.open_btn.pack(side="right")

        # Style comboboxes
        style.configure("TCombobox",
                        fieldbackground=PANEL,
                        background=PANEL,
                        foreground=TEXT,
                        selectbackground=ACCENT,
                        selectforeground="#FFFFFF",
                        bordercolor=PANEL)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _clear_url(self):
        self.url_var.set("")
        self.url_entry.focus()

    def _browse(self):
        d = filedialog.askdirectory(initialdir=self._save_dir)
        if d:
            self._save_dir = d
            self.dir_label.config(text=d)

    def _open_folder(self):
        import subprocess, platform
        if platform.system() == "Windows":
            os.startfile(self._save_dir)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", self._save_dir])
        else:
            subprocess.Popen(["xdg-open", self._save_dir])

    def _on_format_change(self, *_):
        if self.fmt_var.get() == "audio":
            self.qual_menu.config(values=["best", "320k", "192k", "128k", "64k"])
            self.qual_var.set("best")
        else:
            self.qual_menu.config(values=["best", "1080p", "720p", "480p", "360p"])
            self.qual_var.set("best")

    def _set_status(self, msg, color=SUBTEXT):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color)

    def _set_ui_downloading(self, active: bool):
        if active:
            self.dl_btn.config(state="disabled", bg=BORDER)
            self.cancel_btn.config(state="normal")
        else:
            self.dl_btn.config(state="normal", bg=ACCENT)
            self.cancel_btn.config(state="disabled")

    # ── Download logic ─────────────────────────────────────────────────────────

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            self._set_status("Please paste a URL first.", ERROR)
            return

        self._cancel.clear()
        self.progress_var.set(0)
        self._set_ui_downloading(True)
        self._set_status("Starting download…", SUBTEXT)

        self._thread = threading.Thread(
            target=self._download_worker, args=(url,), daemon=True
        )
        self._thread.start()

    def _cancel_download(self):
        self._cancel.set()
        self._set_status("Cancelling…", SUBTEXT)

    def _build_opts(self):
        fmt   = self.fmt_var.get()
        qual  = self.qual_var.get()

        if fmt == "audio":
            # Map quality string → audio bitrate filter
            abr_map = {"320k": "320", "192k": "192", "128k": "128", "64k": "64"}
            abr = abr_map.get(qual)

            postprocessors = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}]
            if abr:
                postprocessors[0]["preferredquality"] = abr

            opts = {
                "format": "bestaudio/best",
                "postprocessors": postprocessors,
                "outtmpl": os.path.join(self._save_dir, "%(title)s.%(ext)s"),
            }
        else:
            # Video quality
            height_map = {"1080p": 1080, "720p": 720, "480p": 480, "360p": 360}
            if qual == "best":
                fmt_selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                h = height_map[qual]
                fmt_selector = (
                    f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]"
                    f"/best[height<={h}][ext=mp4]/best[height<={h}]/best"
                )
            opts = {
                "format": fmt_selector,
                "outtmpl": os.path.join(self._save_dir, "%(title)s.%(ext)s"),
                "merge_output_format": "mp4",
            }
        return opts

    def _download_worker(self, url: str):
        opts = self._build_opts()
        opts["progress_hooks"] = [self._progress_hook]
        opts["quiet"]          = True
        opts["no_warnings"]    = True

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            if not self._cancel.is_set():
                self.after(0, self._on_success)
        except yt_dlp.utils.DownloadCancelled:
            self.after(0, self._on_cancelled)
        except Exception as exc:
            self.after(0, self._on_error, str(exc))

    def _progress_hook(self, d):
        if self._cancel.is_set():
            raise yt_dlp.utils.DownloadCancelled("User cancelled")

        status = d.get("status")
        if status == "downloading":
            total     = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            speed     = d.get("_speed_str", "").strip()
            eta       = d.get("_eta_str", "").strip()
            pct       = (downloaded / total * 100) if total else 0

            msg = f"Downloading… {pct:.1f}%"
            if speed:
                msg += f"  ·  {speed}"
            if eta:
                msg += f"  ·  ETA {eta}"

            self.after(0, self.progress_var.set, min(pct, 99))
            self.after(0, self._set_status, msg, TEXT)

        elif status == "finished":
            fn = os.path.basename(d.get("filename", ""))
            self.after(0, self._set_status, f"Processing: {fn}", SUBTEXT)

    def _on_success(self):
        self.progress_var.set(100)
        self._set_status("Download complete ✓", SUCCESS)
        self._set_ui_downloading(False)

    def _on_cancelled(self):
        self.progress_var.set(0)
        self._set_status("Download cancelled.", SUBTEXT)
        self._set_ui_downloading(False)

    def _on_error(self, msg: str):
        self.progress_var.set(0)
        short = msg[:120] + ("…" if len(msg) > 120 else "")
        self._set_status(f"Error: {short}", ERROR)
        self._set_ui_downloading(False)


if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()
