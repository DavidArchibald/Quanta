import logging
import logging.handlers
import os
import sys


def start_logging():
    log_format = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
    )

    logs = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

    bot_log_file = os.path.join(logs, "bot.log")

    logger = logging.getLogger()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(log_format)

    bot_log_handler = logging.handlers.RotatingFileHandler(
        filename=bot_log_file, maxBytes=2000, backupCount=5
    )
    bot_log_handler.setLevel(logging.INFO)
    bot_log_handler.setFormatter(log_format)

    logger.addHandler(bot_log_handler)
    logger.addHandler(stream_handler)
