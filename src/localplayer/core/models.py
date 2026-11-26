from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass, field

class VideoStatus(str, Enum):
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    READY = "ready"
    FAILED = "failed"

@dataclass
class VideoRecord:
    video_id: str
    title: str
    channel: str
    duration_sec: int
    source_url: str
    status: VideoStatus
    file_path: str | None = None
    thumbnail_path: str | None = None
    subtitle_path: str | None = None
    file_size_bytes: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@dataclass
class PlaybackState:
    video_id: str
    last_position_sec: int = 0
    is_completed: bool = False
    updated_at: str = ""

@dataclass
class TranscriptMatch:
    video_id: str
    video_title: str
    start_sec: int
    cue_text: str