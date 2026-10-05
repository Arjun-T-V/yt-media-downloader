import io
import os
import re
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
import requests
import yt_dlp

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ModernMediaDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Media Downloader Pro")
        self.geometry("720x580")
        self.resizable(False, False)

        self.current_info = None

        # --- Main Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Sidebar Panel
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="⚡ MediaPro",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.pack(padx=20, pady=(25, 10), anchor="w")

        self.desc_label = ctk.CTkLabel(
            self.sidebar,
            text="High quality video & audio downloader",
            font=ctk.CTkFont(size=11),
            text_color="#8A8D93",
            wraplength=160,
            justify="left",
        )
        self.desc_label.pack(padx=20, pady=(0, 20), anchor="w")

        # Sidebar Quick Settings
        self.settings_label = ctk.CTkLabel(
            self.sidebar,
            text="PREFERENCES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#5D626A",
        )
        self.settings_label.pack(padx=20, pady=(15, 5), anchor="w")

        self.format_label = ctk.CTkLabel(
            self.sidebar, text="Format", font=ctk.CTkFont(size=12)
        )
        self.format_label.pack(padx=20, pady=(5, 2), anchor="w")

        self.format_seg = ctk.CTkSegmentedButton(
            self.sidebar,
            values=["Video", "Audio"],
            command=self.toggle_quality_dropdown,
        )
        self.format_seg.set("Video")
        self.format_seg.pack(padx=20, pady=(0, 15), fill="x")

        self.quality_label = ctk.CTkLabel(
            self.sidebar, text="Video Quality", font=ctk.CTkFont(size=12)
        )
        self.quality_label.pack(padx=20, pady=(5, 2), anchor="w")

        self.quality_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["Best Available", "1080p", "720p", "480p", "360p"],
        )
        self.quality_menu.set("Best Available")
        self.quality_menu.pack(padx=20, pady=(0, 15), fill="x")

        # Main Content Area
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(
            row=0, column=1, sticky="nsew", padx=25, pady=20
        )

        # URL Input Row
        self.url_card = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.url_card.pack(fill="x", pady=(0, 15))

        self.url_entry = ctk.CTkEntry(
            self.url_card,
            placeholder_text="Paste YouTube URL here...",
            height=42,
            border_width=0,
            fg_color="transparent",
        )
        self.url_entry.pack(
            side="left", fill="x", expand=True, padx=(15, 5), pady=5
        )

        self.fetch_btn = ctk.CTkButton(
            self.url_card,
            text="Fetch Info",
            width=90,
            height=32,
            corner_radius=8,
            command=self.start_fetch_info,
        )
        self.fetch_btn.pack(side="right", padx=(0, 10))

        # Media Preview Card (Thumbnail & Info)
        self.preview_card = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.preview_card.pack(fill="x", pady=(0, 15))

        self.thumb_label = ctk.CTkLabel(
            self.preview_card,
            text="Paste URL & click Fetch Info",
            width=200,
            height=115,
            corner_radius=8,
            fg_color="#1D2127",
            text_color="#5D626A",
        )
        self.thumb_label.pack(side="left", padx=15, pady=15)

        self.info_frame = ctk.CTkFrame(
            self.preview_card, fg_color="transparent"
        )
        self.info_frame.pack(
            side="left", fill="both", expand=True, padx=(0, 15), pady=15
        )

        self.media_title = ctk.CTkLabel(
            self.info_frame,
            text="No Video Loaded",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=230,
            justify="left",
            anchor="w",
        )
        self.media_title.pack(fill="x", anchor="w")

        self.media_uploader = ctk.CTkLabel(
            self.info_frame,
            text="Channel: --",
            font=ctk.CTkFont(size=11),
            text_color="#8A8D93",
            anchor="w",
        )
        self.media_uploader.pack(fill="x", anchor="w", pady=(5, 0))

        self.media_duration = ctk.CTkLabel(
            self.info_frame,
            text="Duration: --",
            font=ctk.CTkFont(size=11),
            text_color="#8A8D93",
            anchor="w",
        )
        self.media_duration.pack(fill="x", anchor="w")

        # Save Destination Section
        self.path_card = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.path_card.pack(fill="x", pady=(0, 15))

        self.path_entry = ctk.CTkEntry(
            self.path_card,
            height=40,
            border_width=0,
            fg_color="transparent",
        )
        self.path_entry.pack(
            side="left", fill="x", expand=True, padx=(15, 5), pady=5
        )
        self.path_entry.insert(0, os.path.abspath("./"))

        self.browse_btn = ctk.CTkButton(
            self.path_card,
            text="Browse",
            width=80,
            height=32,
            corner_radius=8,
            fg_color="#2B2E33",
            hover_color="#3A3D42",
            command=self.browse_folder,
        )
        self.browse_btn.pack(side="right", padx=(0, 10))

        # Progress Section
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            font=ctk.CTkFont(size=12),
            text_color="#8A8D93",
        )
        self.status_label.pack(anchor="w", pady=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame, height=8, corner_radius=4
        )
        self.progress_bar.pack(fill="x", pady=(0, 20))
        self.progress_bar.set(0)

        # Download CTA Button
        self.download_btn = ctk.CTkButton(
            self.main_frame,
            text="Download Now",
            height=46,
            corner_radius=10,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_download_thread,
        )
        self.download_btn.pack(fill="x")

    def toggle_quality_dropdown(self, selected_mode):
        if selected_mode == "Audio":
            self.quality_menu.configure(state="disabled")
        else:
            self.quality_menu.configure(state="normal")

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, folder_selected)

    def start_fetch_info(self):
        url = self.url_entry.get().strip()
        if not url:
            return

        self.fetch_btn.configure(state="disabled", text="Fetching...")
        self.status_label.configure(text="Fetching video metadata...")

        threading.Thread(
            target=self.fetch_info_thread, args=(url,), daemon=True
        ).start()

    def fetch_info_thread(self, url):
        try:
            ydl_opts = {"skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "Unknown Title")
            uploader = info.get("uploader", "Unknown Channel")
            duration = info.get("duration", 0)
            thumb_url = info.get("thumbnail")

            # Convert duration seconds to MM:SS or HH:MM:SS
            mins, secs = divmod(duration, 60)
            hours, mins = divmod(mins, 60)
            dur_str = (
                f"{hours:02d}:{mins:02d}:{secs:02d}"
                if hours
                else f"{mins:02d}:{secs:02d}"
            )

            # Load thumbnail image
            if thumb_url:
                resp = requests.get(thumb_url)
                img_data = Image.open(io.BytesIO(resp.content))
                ctk_img = ctk.CTkImage(
                    light_image=img_data,
                    dark_image=img_data,
                    size=(180, 100),
                )
            else:
                ctk_img = None

            # Update UI on main thread
            self.after(
                0, self.update_preview_ui, title, uploader, dur_str, ctk_img
            )

        except Exception as e:
            self.after(
                0,
                lambda: self.status_label.configure(
                    text="Failed to load video info.", text_color="#E74C3C"
                ),
            )
        finally:
            self.after(
                0,
                lambda: self.fetch_btn.configure(
                    state="normal", text="Fetch Info"
                ),
            )

    def update_preview_ui(self, title, uploader, dur_str, ctk_img):
        self.media_title.configure(text=title)
        self.media_uploader.configure(text=f"Channel: {uploader}")
        self.media_duration.configure(text=f"Duration: {dur_str}")

        if ctk_img:
            self.thumb_label.configure(image=ctk_img, text="")

        self.status_label.configure(
            text="Video details loaded successfully!", text_color="#2ECC71"
        )

    def progress_hook(self, d):
        if d["status"] == "downloading":
            p_str = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                clean_p_str = re.sub(r"\x1b\[[0-9;]*m", "", p_str)
                percentage = float(clean_p_str)

                self.progress_bar.set(percentage / 100)
                speed = d.get("_speed_str", "N/A")
                eta = d.get("_eta_str", "N/A")

                self.status_label.configure(
                    text=f"Downloading: {percentage:.1f}%  •  Speed: {speed}  •  ETA: {eta}",
                    text_color="#3498DB",
                )
            except ValueError:
                pass

        elif d["status"] == "finished":
            self.progress_bar.set(1.0)
            self.status_label.configure(
                text="Processing and saving media...", text_color="#2ECC71"
            )

    def start_download_thread(self):
        url = self.url_entry.get().strip()
        save_path = self.path_entry.get().strip()

        if not url:
            messagebox.showwarning(
                "Input Error", "Please enter a valid YouTube URL."
            )
            return

        self.download_btn.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)

        threading.Thread(
            target=self.download_video, args=(url, save_path), daemon=True
        ).start()

    def download_video(self, url, save_path):
        mode = self.format_seg.get()
        quality = self.quality_menu.get()

        if mode == "Audio":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": f"{save_path}/%(title)s.%(ext)s",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "progress_hooks": [self.progress_hook],
            }
        else:
            if quality == "1080p":
                fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif quality == "720p":
                fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            elif quality == "480p":
                fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"
            elif quality == "360p":
                fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
            else:
                fmt = "bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt,
                "outtmpl": f"{save_path}/%(title)s.%(ext)s",
                "progress_hooks": [self.progress_hook],
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(
                text="Download Complete!", text_color="#2ECC71"
            )
            messagebox.showinfo("Success", "Media downloaded successfully!")
        except Exception as e:
            self.status_label.configure(
                text="Download failed.", text_color="#E74C3C"
            )
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
        finally:
            self.download_btn.configure(
                state="normal", text="Download Now"
            )


if __name__ == "__main__":
    app = ModernMediaDownloader()
    app.mainloop()