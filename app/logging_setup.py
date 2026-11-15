import logging
import sys


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if any(getattr(handler, "_app_stdout_handler", False)
           for handler in root_logger.handlers):
        return

    handler = logging.StreamHandler(sys.stdout)
    handler._app_stdout_handler = True
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    ))

    root_logger.addHandler(handler)