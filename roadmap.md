# Project Goal For V1.0.0

This file contains what is coming up in the next version **(v1.0.0)** and what's out.

## What's In
 - **Decoupled Architecture** - maintained seperation of concerns by dividing the code into respective responsibilities.
 - **Reliable Media & Subtitle Downloader** - Downloading video, thumbnails and auto-generated/manual subtitles (.vtt or .srt) using `yt-dlp` library into organized local directories.
 - **SQLite State & Playback Tracker** - A local database tracking every video's status (QUEUED, DOWNLOADING, READY, FAILED), file size, duration, and last_watched_second so users can resume where they left off.
 - **Instant Transcript Search (SQLite FTS5)** - Parse the downloaded subtitle file into clean timestamped chunks and index them in SQLite's built-in FTS5 virtual table. Searching "binary search" returns every video and exact timestamp where that phrase was spoken—completely offline.
 - **Production Grade Logging** - A rotating log file recording download starts, retries, subtitle parsing errors, and database events, paired with clean terminal output.
 - **Interface** - There will be both CLI and GUI Interface (made using Flet) for this application.

## What's Out (will come in the upcoming versions)
 - **Cloud Sync (v1.5)** - Option to store videos on your cloud storage (Supported: Google Cloud, One Drive and DropBox)
 - **LAN (Wi-Fi) Peer Sharing (v2.0)** - Easily share downloaded videos over the wifi to another device connected to the same wifi