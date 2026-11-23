import logging
from logging.handlers import RotatingFileHandler

from localplayer.core.paths import get_logs_dir

def console_logger(verbose: bool = False) -> logging.StreamHandler:
    """Returns the streamhandler for logger"""
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_logger.setFormatter(formatter)

    return console_logger

def file_logger(verbose: bool = False) -> RotatingFileHandler:
    """Returns the file handler for logger"""
    file_logger = RotatingFileHandler(
        filename=get_logs_dir() / "log.log",
        maxBytes=2000000,
        backupCount=3,
        encoding="UTF-8"
    )
    file_logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_logger.setFormatter(formatter)

    return file_logger

def setup_logger(console_logger_verbose: bool = False, file_logger_verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    con_logger = console_logger(verbose=True if console_logger_verbose else False)
    fil_logger = file_logger(verbose=True if file_logger_verbose else False)

    logger.addHandler(con_logger)
    logger.addHandler(fil_logger)

    return logger