import os
import pygame
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from mutagen.id3 import ID3, TIT2, TPE1, TALB
from pygame import mixer
from PIL import Image, ImageTk
import random

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("800x600")

        self.playlist = []
        self.current_track = 0
        self.paused = False
        self.shuffle = False
        self.repeat = False
        self.volume = 0.5
        self.timer_duration = 0  # Duration in seconds

        mixer.init()
        self.load_playlist()

        self.create_ui()

    def create_ui(self):
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Create playlist frame
        playlist_frame = tk.Frame(main_frame)
        playlist_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Create listbox for playlist
        self.playlist_listbox = tk.Listbox(playlist_frame, selectmode=tk.SINGLE)
        self.playlist_listbox.pack(fill="both", expand=True)
        self.playlist_listbox.bind("<<ListboxSelect>>", self.play_selected_track)

        # Create buttons frame
        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Load button
        load_button = tk.Button(buttons_frame, text="Load Playlist", command=self.load_playlist)
        load_button.pack(fill="x")

        # Play/Pause button
        self.play_pause_button = tk.Button(buttons_frame, text="Play", command=self.toggle_play_pause)
        self.play_pause_button.pack(fill="x")

        # Previous button
        previous_button = tk.Button(buttons_frame, text="Previous", command=self.play_previous_track)
        previous_button.pack(fill="x")

        # Next button
        next_button = tk.Button(buttons_frame, text="Next", command=self.play_next_track)
        next_button.pack(fill="x")

        # Stop button
        stop_button = tk.Button(buttons_frame, text="Stop", command=self.stop_track)
        stop_button.pack(fill="x")

        # Clear Playlist button
        clear_button = tk.Button(buttons_frame, text="Clear Playlist", command=self.clear_playlist)
        clear_button.pack(fill="x")

        # Shuffle button
        shuffle_button = tk.Button(buttons_frame, text="Shuffle", command=self.toggle_shuffle)
        shuffle_button.pack(fill="x")

        # Repeat button
        repeat_button = tk.Button(buttons_frame, text="Repeat", command=self.toggle_repeat)
        repeat_button.pack(fill="x")

        # Loop button
        loop_button = tk.Button(buttons_frame, text="Loop", command=self.toggle_loop)
        loop_button.pack(fill="x")

        # Volume control
        volume_label = tk.Label(buttons_frame, text="Volume:")
        volume_label.pack(fill="x")
        self.volume_scale = ttk.Scale(buttons_frame, from_=0, to=1, command=self.change_volume)
        self.volume_scale.set(self.volume)
        self.volume_scale.pack(fill="x")

        # Timer control
        timer_label = tk.Label(buttons_frame, text="Timer (min):")
        timer_label.pack(fill="x")
        self.timer_entry = ttk.Entry(buttons_frame)
        self.timer_entry.pack(fill="x")
        set_timer_button = tk.Button(buttons_frame, text="Set Timer", command=self.set_timer)
        set_timer_button.pack(fill="x")

        # Album art
        self.album_art_label = tk.Label(buttons_frame)
        self.album_art_label.pack()

        # Track info label
        self.track_info_label = tk.Label(buttons_frame, text="", wraplength=200)
        self.track_info_label.pack(fill="x")

        # Duration and current time labels
        self.duration_label = tk.Label(buttons_frame, text="Duration: 00:00")
        self.duration_label.pack(fill="x")
        self.current_time_label = tk.Label(buttons_frame, text="Current: 00:00")
        self.current_time_label.pack(fill="x")

        # Total tracks label
        self.total_tracks_label = tk.Label(buttons_frame, text="Total Tracks: 0")
        self.total_tracks_label.pack(fill="x")

        # Progress bar
        self.progress_bar = ttk.Progressbar(buttons_frame, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(fill="x")

        # Available audio devices
        audio_devices_label = tk.Label(buttons_frame, text="Audio Output:")
        audio_devices_label.pack(fill="x")
        self.audio_devices_combobox = ttk.Combobox(buttons_frame)
        self.audio_devices_combobox.pack(fill="x")

        # Initialize audio devices
        self.init_audio_devices()

        # Search and filter
        search_label = tk.Label(playlist_frame, text="Search:")
        search_label.pack(fill="x")
        self.search_entry = ttk.Entry(playlist_frame)
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.filter_playlist)

        # Display current track
        current_track_label = tk.Label(playlist_frame, text="Now Playing:", font=("Arial", 10, "bold"))
        current_track_label.pack(fill="x")
        self.current_track_label = tk.Label(playlist_frame, text="", font=("Arial", 10))
        self.current_track_label.pack(fill="x")

        # Metadata and Playlist management buttons
        metadata_label = tk.Label(playlist_frame, text="Track Metadata:", font=("Arial", 10, "bold"))
        metadata_label.pack(fill="x")

        metadata_frame = tk.Frame(playlist_frame)
        metadata_frame.pack(fill="x")

        title_label = tk.Label(metadata_frame, text="Title:")
        title_label.grid(row=0, column=0, sticky="e")
        self.title_entry = ttk.Entry(metadata_frame)
        self.title_entry.grid(row=0, column=1)

        artist_label = tk.Label(metadata_frame, text="Artist:")
        artist_label.grid(row=1, column=0, sticky="e")
        self.artist_entry = ttk.Entry(metadata_frame)
        self.artist_entry.grid(row=1, column=1)

        album_label = tk.Label(metadata_frame, text="Album:")
        album_label.grid(row=2, column=0, sticky="e")
        self.album_entry = ttk.Entry(metadata_frame)
        self.album_entry.grid(row=2, column=1)

        update_metadata_button = tk.Button(playlist_frame, text="Update Metadata", command=self.update_metadata)
        update_metadata_button.pack(fill="x")

        create_playlist_button = tk.Button(playlist_frame, text="Create Playlist", command=self.create_playlist)
        create_playlist_button.pack(fill="x")

        self.update_playlist_ui()

    def init_audio_devices(self):
        pygame.mixer.init()
        audio_info = pygame.mixer.get_init()
        available_audio = pygame.mixer.get_num_audio_devices()
        audio_devices = pygame.mixer.get_audio_device_info()

        self.audio_devices_combobox["values"] = [device["name"] for device in audio_devices]
        self.audio_devices_combobox.set(audio_info[1])

    def load_playlist(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("MP3 files", "*.mp3")])
        if file_paths:
            self.playlist = file_paths
            self.current_track = 0
            self.update_playlist_ui()
            self.play_track()

    def update_playlist_ui(self):
        self.playlist_listbox.delete(0, tk.END)
        for i, track in enumerate(self.playlist):
            self.playlist_listbox.insert(i, os.path.basename(track))
        self.total_tracks_label.config(text=f"Total Tracks: {len(self.playlist)}")
        self.current_track_label.config(text=f"Now Playing: {os.path.basename(self.playlist[self.current_track])}")

    def filter_playlist(self, event):
        query = self.search_entry.get().strip().lower()
        filtered_playlist = [track for track in self.playlist if query in os.path.basename(track).lower()]
        self.playlist_listbox.delete(0, tk.END)
        for i, track in enumerate(filtered_playlist):
            self.playlist_listbox.insert(i, os.path.basename(track))

    def play_selected_track(self, event):
        selected_track = self.playlist_listbox.curselection()
        if selected_track:
            self.current_track = selected_track[0]
            self.play_track()

    def play_track(self):
        if self.playlist:
            track = self.playlist[self.current_track]
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play()
            self.update_track_info(track)
            self.update_duration()
            self.play_pause_button.config(text="Pause")
            self.paused = False

    def update_track_info(self, track):
        audio = ID3(track)
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, audio.get(TIT2, ""))
        self.artist_entry.delete(0, tk.END)
        self.artist_entry.insert(0, audio.get(TPE1, ""))
        self.album_entry.delete(0, tk.END)
        self.album_entry.insert(0, audio.get(TALB, ""))
        self.update_album_art(track)

    def update_album_art(self, track):
        pass  

    def update_duration(self):
        audio = MP3(self.playlist[self.current_track])
        total_time = int(audio.info.length)
        self.duration_label.config(text=f"Duration: {self.format_time(total_time)}")
        self.progress_bar["maximum"] = total_time

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02}:{seconds:02}"

    def toggle_play_pause(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.play_pause_button.config(text="Pause")
            self.paused = False
        else:
            pygame.mixer.music.pause()
            self.play_pause_button.config(text="Play")
            self.paused = True

    def play_previous_track(self):
        if len(self.playlist) > 1:
            if self.current_track > 0:
                self.current_track -= 1
            else:
                self.current_track = len(self.playlist) - 1
            self.play_track()

    def play_next_track(self):
        if len(self.playlist) > 1:
            if self.current_track < len(self.playlist) - 1:
                self.current_track += 1
            else:
                self.current_track = 0
            self.play_track()

    def stop_track(self):
        pygame.mixer.music.stop()
        self.play_pause_button.config(text="Play")
        self.paused = False

    def clear_playlist(self):
        self.playlist = []
        self.update_playlist_ui()

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.shuffle_playlist()
        self.update_playlist_ui()

    def shuffle_playlist(self):
        random.shuffle(self.playlist)

    def toggle_repeat(self):
        self.repeat = not self.repeat

    def toggle_loop(self):
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        if self.repeat:
            pygame.mixer.music.set_endevent(pygame.constants.USEREVENT + 1)

    def change_volume(self, value):
        self.volume = float(value)
        pygame.mixer.music.set_volume(self.volume)

    def set_timer(self):
        try:
            minutes = int(self.timer_entry.get())
            self.timer_duration = minutes * 60
            if self.timer_duration > 0:
                self.root.after(self.timer_duration * 1000, self.stop_track)
                messagebox.showinfo("Timer Set", f"Player will stop in {minutes} minutes.")
            else:
                messagebox.showerror("Invalid Timer", "Please enter a valid timer duration.")
        except ValueError:
            messagebox.showerror("Invalid Timer", "Please enter a valid timer duration.")

    def update_metadata(self):
        track = self.playlist[self.current_track]
        audio = ID3(track)
        audio["TIT2"] = TIT2(encoding=3, text=self.title_entry.get())
        audio["TPE1"] = TPE1(encoding=3, text=self.artist_entry.get())
        audio["TALB"] = TALB(encoding=3, text=self.album_entry.get())
        audio.save()

    def create_playlist(self):
        playlist_name = filedialog.asksaveasfilename(defaultextension=".m3u", filetypes=[("M3U Playlist", "*.m3u")])
        if playlist_name:
            with open(playlist_name, "w") as playlist_file:
                for track in self.playlist:
                    playlist_file.write(f"{track}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
