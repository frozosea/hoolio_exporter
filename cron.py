from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Callable
from dataclasses import dataclass

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


@dataclass()
class Time:
    Hours: str | int
    Minutes: str | int
    Seconds: str | int


@dataclass()
class Job:
    Id: any
    Func: Callable
    Time: Time


class ICronManager(ABC):
    @abstractmethod
    def add(self, task_id: any, fn: Callable, **kwargs) -> Job:
        ...

    @abstractmethod
    def remove(self, task_id: any) -> None:
        ...

    @abstractmethod
    def start(self):
        ...


class CronManager(ICronManager):

    def __init__(self):
        self.__manager = AsyncIOScheduler()

    def add(self, task_id: any, fn: Callable, *args, **kwargs) -> Job:
        self.__manager.add_job(func=fn, id=str(task_id), replace_existing=False, jobstore="default", *args, **kwargs)
        return

    def remove(self, task_id: any) -> None:
        self.__manager.remove_job(task_id)

    def start(self):
        self.__manager.start()
