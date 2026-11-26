#NOTE: Test Runs | Not Production Code

from localplayer.core.logger import setup_logger
from localplayer.core.paths import ensure_user_config
from localplayer.core.database import DatabaseManager
from localplayer.core.models import VideoRecord, VideoStatus


def main() -> None:
    logger = setup_logger(file_logger_verbose=True)
    settings_file = ensure_user_config()
    logger.debug("Settings file is ready at: %s", settings_file)
    database = DatabaseManager()
    sample_video = VideoRecord(
        video_id="sample-video-1",
        title="About Python",
        channel="pythonorg",
        duration_sec=300,
        source_url="https://youtube.com/watch?v=abcdefgh",
        status=VideoStatus.DOWNLOADING,
        file_path="~/.localplayer/example",
        thumbnail_path="~/.localplayer/example/thumbnail.jpg",
        subtitle_path="~/.localplayer/example/subtitles/subtitle1.txt"
    )
    database.upsert_video(sample_video)
    database.list_videos()
    database.update_video(video_id="sample-video-1", status=VideoStatus.READY)
    database.index_transcript("sample-video-1", cues=[(100, "Welcome to our new channel"), (500, "Python was made by Guido van rosssum.")])
    query = "Guido van"
    matches = database.search_transcripts(query)
    logger.info("localplayer | Found %s matches for query %s | matches=%s", len(matches), query, matches)
    logger.info("LocalPlayer is ready.")

if __name__ == "__main__":
    main()