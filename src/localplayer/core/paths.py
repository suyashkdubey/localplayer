import shutil
from pathlib import Path

def get_app_dir() -> Path:
    """
    Returns the path for the app's storage directory in the respective OS
    """
    app_dir = Path.home() / ".localplayer"
    Path.mkdir(app_dir, parents=True, exist_ok=True)

    return app_dir

def get_logs_dir() -> Path:
    """
    Returns the path for the logs directory inside of the app's directory in the respective OS
    """
    app_dir = get_app_dir()
    logs_dir = app_dir / "logs/"
    Path.mkdir(logs_dir, parents=True, exist_ok=True)

    return logs_dir

def get_downloads_path() -> Path:
    """
    Returns the path for the downloads directory inside of the app's directory in the respective OS
    """
    app_dir = get_app_dir()
    downloads_dir = app_dir / "downloads/"
    Path.mkdir(downloads_dir, parents=True, exist_ok=True)

    return downloads_dir

def get_db_path() -> Path:
    """
    Returns the path for the database directory inside of the app's directory in the respective OS
    """
    app_dir = get_app_dir()
    db_path = app_dir / "database" / "vault.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return db_path

def ensure_user_config() -> Path:
    app_dir = get_app_dir()
    settings_file = app_dir / "settings.toml"
    if not settings_file.exists():
        default_settings = Path(__file__).resolve().parent.parent / "default_settings.toml"
        shutil.copyfile(default_settings, settings_file)

    return settings_file