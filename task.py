import time
from typing import Type
from typing import Coroutine
from abc import ABC
from abc import abstractmethod
from logger import ILogger


class IPublisherRetryOnExceptionTaskProvider(ABC):
    @abstractmethod
    def get_task(self, fn, retry_number: int,
                 logger: Type[ILogger], sleep_on_exception: int, *args, **kwargs) -> Coroutine:
        ...


class PublisherRetryOnExceptionTaskProvider(IPublisherRetryOnExceptionTaskProvider):
    def get_task(self, fn, retry_number: int,
                 logger: Type[ILogger], sleep_on_exception: int, *args, **kwargs) -> Coroutine:
        async def task():
            for i in range(1, retry_number):
                try:
                    await fn(*args, **kwargs)
                    break
                except Exception as e:
                    logger.error(f"publisher: {fn.__name__} retry on exception number: {i} error: {str(e)}")
                    time.sleep(sleep_on_exception)
                    continue

        return task
