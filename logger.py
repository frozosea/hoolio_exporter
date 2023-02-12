import sys
import os

from loguru import logger
from abc import ABC
from abc import abstractmethod


class ILogger(ABC):
    @abstractmethod
    def info(self, log: str) -> 'ILogger':
        ...

    @abstractmethod
    def warning(self, log: str) -> 'ILogger':
        ...

    @abstractmethod
    def error(self, log: str) -> 'ILogger':
        ...

    @abstractmethod
    def debug(self, log: str) -> 'ILogger':
        ...


class _WriterToNone:
    def write(self, message) -> None:
        pass


class Logger(ILogger):
    def __init__(self, is_to_file: bool, dir_name: str):
        logger.add(f"{dir_name}/info.log" if is_to_file else _WriterToNone(), format="{time} {level} {message}",
                   filter=lambda record: record["level"].name == "INFO", level="INFO")
        logger.add(f"{dir_name}/error.log" if is_to_file else _WriterToNone(), format="{time} {level} {message}",
                   filter=lambda record: record["level"].name == "ERROR", level="ERROR")
        logger.add(f"{dir_name}/warning.log" if is_to_file else _WriterToNone(), format="{time} {level} {message}",
                   filter=lambda record: record["level"].name == "WARNING", level="WARNING")
        logger.add(f"{dir_name}/debug.log" if is_to_file else _WriterToNone(), format="{time} {level} {message}",
                   filter=lambda record: record["level"].name == "DEBUG", level="DEBUG")
        logger.add(f"{dir_name}/fatal.log" if is_to_file else _WriterToNone(), format="{time} {level} {message}",
                   filter=lambda record: record["level"].name == "CRITICAL", level="CRITICAL")
        self.__logger = logger

    def info(self, log: str) -> ILogger:
        try:
            self.__logger.info(log)
            return self
        except Exception as e:
            self.error(str(e))

    def warning(self, log: str) -> ILogger:
        try:
            self.__logger.warning(log)
            return self
        except Exception as e:
            self.error(str(e))

    def error(self, log: str) -> ILogger:
        try:
            self.__logger.error(log)
            return self
        except Exception as e:
            print(e)

    def debug(self, log: str) -> ILogger:
        try:
            self.__logger.debug(log)
            return self
        except Exception as e:
            self.error(str(e))


if __name__ == '__main__':
    Logger(True, "logs/custom_logs").info("info log").error("error log").debug("debug log").warning("warning log")
