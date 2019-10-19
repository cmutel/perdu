from . import base_dir
import datetime
import json
import logging
import time


logs_dir = base_dir / "logs"
logs_dir.mkdir(exist_ok=True)


class JsonFormatter(logging.Formatter):
    """Uses code from https://github.com/madzak/python-json-logger/ under BSD license"""

    def format(self, record):
        assert isinstance(record.msg, dict)
        message_dict = record.msg
        message_dict["time"] = time.time()
        return json.dumps(message_dict, ensure_ascii=False)


def create_job_log(output_dir, level=logging.INFO):
    filename = u"%s-%s.log" % (
        name,
        datetime.datetime.now().strftime("%d-%B-%Y-%I-%M%p"),
    )
    logger = logging.getLogger("perdu-job")
    logger.propagate = False
    formatter = JsonFormatter()
    handler = logging.FileHandler(logs_dir / filename, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return filepath


def close_log(log):
    """Detach log handlers; flush to disk"""
    handlers = log.handlers[:]
    for handler in handlers:
        handler.close()
        log.removeHandler(handler)
