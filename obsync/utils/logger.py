import logging
import os
from pathlib import PurePath
from typing import Optional, Union

logger_initialized = {}


def get_logger(
    name: str = "ob-sync",
    log_file: Optional[Union[str, PurePath]] = None,
    log_level: int = logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)
    if name in logger_initialized:
        return logger

    logger.setLevel(log_level)

    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    sh_handler = logging.StreamHandler()
    sh_handler.setFormatter(log_format)
    logger.addHandler(sh_handler)

    if log_file is not None:
        if os.path.isdir(log_file):
            raise ValueError(
                "`log_file` must be a file, but got: {}".format(log_file)
            )
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        th_handler = logging.FileHandler(log_file, encoding="utf-8")
        th_handler.setFormatter(log_format)
        logger.addHandler(th_handler)

    logger_initialized[name] = True

    return logger
