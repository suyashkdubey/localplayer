import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone

from localplayer.core.paths import get_db_path
from localplayer.core.models import VideoStatus, VideoRecord, TranscriptMatch

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: Path | None = None) -> None:
        self._foreign_key_turned_on = False
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if self._foreign_key_turned_on is False:
            logger.debug("Sqlite3 | Turning on foreign_keys | PRAGMA foreign_keys = ON")
            self._foreign_key_turned_on = True
        conn.execute("PRAGMA foreign_keys = ON")

        return conn

    def _init_db(self) -> None:
        logger.info("Sqlite3 | Initializing database | path=%s", self.db_path)

        try:
            with self._get_connection() as conn:
                logger.debug("Sqlite3 | Switching journal_mode to WAL | PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS videos (
                        video_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        duration_sec INTEGER NOT NULL DEFAULT 0,
                        source_url TEXT NOT NULL,
                        status TEXT NOT NULL,
                        file_path TEXT,
                        thumbnail_path TEXT,
                        subtitle_path TEXT,
                        file_size_bytes INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS playback_state (
                        video_id TEXT PRIMARY KEY REFERENCES videos(video_id) ON DELETE CASCADE,
                        last_position_sec INTEGER NOT NULL DEFAULT 0,
                        is_completed INTEGER NOT NULL DEFAULT 0,
                        updated_at TEXT NOT NULL
                    );

                    CREATE VIRTUAL TABLE IF NOT EXISTS transcript_fts USING fts5(
                        video_id UNINDEXED,
                        start_sec UNINDEXED,
                        cue_text
                    );
                    """
                )
                conn.commit()
            logger.info("Sqlite3 | Database created successfully | path=%s", self.db_path)

        except Exception as exc:
            logger.error("Sqlite3 | An error occured while initializing database | ERROR=%s", exc)
            raise

    def _row_to_video(self, row: sqlite3.Row) -> VideoRecord:
        return VideoRecord(
            video_id=row["video_id"],
            title=row["title"],
            channel=row["channel"],
            duration_sec=row["duration_sec"],
            source_url=row["source_url"],
            status=VideoStatus(row["status"]),
            file_path=row["file_path"],
            thumbnail_path=row["thumbnail_path"],
            subtitle_path=row["subtitle_path"],
            file_size_bytes=int(row["file_size_bytes"]),
            created_at=row["created_at"]
        )

    def upsert_video(self, video: VideoRecord) -> None:
        try:
            with self._get_connection() as conn:
                logger.info("Sqlite3 | Upserting a video in the database")
                conn.execute("""
                  INSERT INTO videos (video_id, title, channel, duration_sec, source_url, status, file_path, thumbnail_path, subtitle_path, file_size_bytes, created_at)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                  ON CONFLICT(video_id) DO UPDATE SET
                    title = excluded.title,
                    channel = excluded.channel,
                    duration_sec = excluded.duration_sec,
                    status = excluded.status;
                """, (video.video_id, video.title, video.channel, video.duration_sec, video.source_url, video.status, video.file_path, video.thumbnail_path, video.subtitle_path, video.file_size_bytes, video.created_at))

                conn.execute("""
                 INSERT OR IGNORE INTO playback_state (video_id, updated_at) VALUES (?, ?)
                """, (video.video_id, video.created_at))

                conn.commit()

        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while upserting the video | ERROR=%s", exc)
            raise

        except Exception as e:
            logger.error("Sqlite3 | An error occured while upserting the video | ERROR=%s", e)
            raise RuntimeError(f"An error occured while upserting the video in the database | ERROR={e}")

    def update_video(self, video_id:str, status: VideoStatus, file_path: str | None = None, thumbnail_path: str | None = None, subtitle_path: str | None = None, file_size_bytes: int = 0) -> None:
        try:
            with self._get_connection() as conn:
                logger.info("Sqlite3 | Updating a video in the database")
                conn.execute("""
                    UPDATE videos SET status = ?, file_path = COALESCE(?, file_path), thumbnail_path = COALESCE(?, thumbnail_path), subtitle_path = COALESCE(?,subtitle_path), file_size_bytes = COALESCE(?, file_size_bytes) WHERE video_id = ?
                """, (status, file_path, thumbnail_path, subtitle_path, file_size_bytes, video_id))

                conn.commit()

        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while updating the video | ERROR=%s", exc)
            raise

        except Exception as e:
            logger.error("Sqlite3 | An error occured while updating the video | ERROR=%s", e)
            raise RuntimeError(f"An error occured while updating the video in the database | ERROR={e}")

    def get_video(self, video_id: str) -> VideoRecord | None:
        try:
            with self._get_connection() as conn:
                logger.info("Sqlite3 | Fetching a video from the database")
                cursor = conn.execute("""
                    SELECT * FROM videos WHERE video_id = ?;
                """, (video_id,))
                conn.commit()
                row = cursor.fetchone()

            return self._row_to_video(row) if row is not None else None

        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while fetching the video | ERROR=%s", exc)
            raise

        except Exception as e:
            logger.error("Sqlite3 | An error occured while fetching the video | ERROR=%s", e)
            raise RuntimeError(f"An error occured while fetching the video in the database | ERROR={e}")

    def list_videos(self, status: VideoStatus | None = None) -> list[VideoRecord]:
        try:
            if status is not None:
                logger.info("Sqlite3 | Fetching all videos | FILTER=%s", status)
                with self._get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC
                    """, (status,))
                    conn.commit()
                    rows = cursor.fetchall()

                return [self._row_to_video(row) for row in rows]
            else:
                logger.info("Sqlite3 | Fetching all videos | FILTER=%s", None)
                with self._get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT * FROM videos ORDER BY created_at DESC
                    """)
                    conn.commit()
                    rows = cursor.fetchall()

                return [self._row_to_video(row) for row in rows]

        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while fetching the videos | FILTER=%s | ERROR=%s", status if not None else None, exc)

        except Exception as e:
            logger.error("Sqlite3 | An error occured while fetching the videos | FILTER=%s | ERROR=%s", status if not None else None, e)
            raise RuntimeError(f"An error occured while fetching the videos | FILTER={status if not None else None} | ERROR={e}")

    def update_playback(self, video_id: str, position_sec: int, is_completed: bool = False) -> None:
        try:
            with self._get_connection() as conn:
                logger.info("Sqlite3 | Updating a video")
                conn.execute("""
                    UPDATE playback_state SET last_position_sec = ?, is_completed = ?, updated_at = ? WHERE video_id = ?
                """, (position_sec, int(is_completed), datetime.now(timezone.utc).isoformat(), video_id))

                conn.commit()

        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while updating a playback state | ERROR=%s", exc)

        except Exception as e:
            logger.error("Sqlite3 | An error occured while updating a playback state | ERROR=%s", e)
            raise RuntimeError(f"An error occured while updating a playback state | ERROR={e}")

    def index_transcript(self, video_id: str, cues: list[tuple[int, str]]) -> None:
        try:
            with self._get_connection() as conn:
                logger.info("Sqlite3 | Searching the database for the video")
                conn.execute("""
                    DELETE FROM transcript_fts WHERE video_id = ?
                """, (video_id,))
                logger.debug("Sqlite3 | Deleted old transcript to replace by fresh one")
                rows = [(video_id, start_sec, cue_text) for start_sec, cue_text in cues]
                conn.executemany("INSERT INTO transcript_fts (video_id, start_sec, cue_text) VALUES (?, ?, ?)", rows)

                conn.commit()
        
        except sqlite3.OperationalError as exc:
            logger.error("Sqlite3 | An error occured while searching the database | ERROR=%s", exc)

        except Exception as e:
            logger.error("Sqlite3 | An error occured while searching the database | ERROR=%s", e)
            raise RuntimeError(f"Sqlite3 | An error occured while updating a playback state | ERROR={e}")

    def search_transcripts(self, query: str) -> list[TranscriptMatch]:
        if not query.strip():
            logger.info("localplayer | Pass a valid query to search for video")
            return []

        try:
            with self._get_connection() as conn:
                logger.info("localplayer | Searching for the provided query | QUERY=%s", query)
                cursor = conn.execute("""
                    SELECT t.video_id, v.title, t.start_sec, t.cue_text
                    FROM transcript_fts t
                    JOIN videos v ON t.video_id = v.video_id
                    WHERE transcript_fts MATCH ?
                    LIMIT 50;
                """, (query,))
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append(TranscriptMatch(video_id=row["video_id"], video_title=row["title"], start_sec=int(row["start_sec"]), cue_text=row["cue_text"]))

                return result
        
        except sqlite3.OperationalError as exc:
            logger.warning("localplayer | Pass a valid query to search for video | ERROR=%s", exc)
            return []

        except Exception as e:
            logger.error("localplayer | An error occured while searching for the query | ERROR=%s", e)
            raise RuntimeError(f"localplayer | An error occured while searching for the query | ERROR={e}")