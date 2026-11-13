import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(config):

    log_file = Path(config["logging"]["file"])

    log_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger("linux_system_monitor")

    logger.setLevel(
        getattr(
            logging,
            config["logging"]["level"].upper(),
            logging.INFO
        )
    )

    logger.propagate = False

    if logger.handlers:
        return logger

    handler = RotatingFileHandler(
        log_file,
        maxBytes=config["logging"]["max_bytes"],
        backupCount=config["logging"]["backup_count"]
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

