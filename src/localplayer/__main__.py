from localplayer.core.logger import setup_logger
from localplayer.core.paths import ensure_user_config


def main() -> None:
    logger = setup_logger(file_logger_verbose=True)
    settings_file = ensure_user_config()
    logger.debug("Settings file is ready at: %s", settings_file)
    logger.info("LocalPlayer is ready.")


if __name__ == "__main__":
    main()