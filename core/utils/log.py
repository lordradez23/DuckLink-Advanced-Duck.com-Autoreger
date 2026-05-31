import logging

from loguru import logger
import sys
import asyncio
import contextvars


class InterceptHandler(logging.Handler):
    def __init__(self, log_prefix_var):
        super().__init__()
        self.log_prefix_var = log_prefix_var

    def emit(self, record):
        level = logger.level(record.levelname).name if record.levelname in logger._core.levels else record.levelno
        prefix_log_message = self.log_prefix_var.get()

        logger.bind(prefix_log_message=prefix_log_message).opt(depth=6, exception=record.exc_info).log(level,
                                                                                                       record.getMessage())


class XLogger:
    def __init__(self, logger):
        self.logger = logger
        self.logger.remove()

        if os.environ.get("SILENT_MODE", "False").lower() != "true":
            self.logger.add(
                sys.stdout,
            level="INFO",
            format="<green>{time:YYYY-MM-DDTHH:mm:ss.SSSZ}</green> | "
                   "<level>{level: <8}</level> | <light-red>{extra[prefix_log_message]}</light-red>"
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True,
            enqueue=True
        )
        self.logger.add(
            "application.log",
            level="DEBUG",
            format="{time} - {name}:{function}:{line} - {level} - {extra[prefix_log_message]}{message}",
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            serialize=os.environ.get("JSON_LOGS", "False").lower() == "true",
            enqueue=True
        )

        self.log_prefix_var = contextvars.ContextVar("log_prefix_var", default="")
        logging.basicConfig(handlers=[InterceptHandler(self.log_prefix_var)], level=logging.DEBUG)

    def _bind(self):
        return self.logger.bind(prefix_log_message=self.log_prefix_var.get())

    def info(self, message):
        self.logger.opt(depth=1).bind(prefix_log_message=self.log_prefix_var.get()).info(message)

    def debug(self, message):
        self.logger.opt(depth=1).bind(prefix_log_message=self.log_prefix_var.get()).debug(message)

    def warning(self, message):
        self.logger.opt(depth=1).bind(prefix_log_message=self.log_prefix_var.get()).warning(message)

    def error(self, message):
        self.logger.opt(depth=1).bind(prefix_log_message=self.log_prefix_var.get()).error(message)

    def critical(self, message):
        self.logger.opt(depth=1).bind(prefix_log_message=self.log_prefix_var.get()).critical(message)


xlogger = XLogger(logger)


success_rate_tracker = {'success': 0, 'fail': 0}


# Feature 16: detailed proxy fail stats
proxy_fail_tracker = {}


# Feature 17: Latency tracking list
latency_tracker = []


# Feature 18: Captcha stats
captcha_stats = {'total_time': 0, 'solves': 0}


def export_log_csv(file_path):
    pass # Feature 19: Export stub
