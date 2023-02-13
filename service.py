import datetime
from abc import ABC
from abc import abstractmethod
from typing import Type
from publisher import MainPublisher
from repository import IPropertyRepository
from logger import ILogger
from cron import ICronManager
from entity import Property
from description import IDescriptionGenerator


class IService(ABC):
    @abstractmethod
    async def publish(self, property: Property) -> None:
        ...


class Service(IService):
    def __init__(self, publisher: MainPublisher, repository: Type[IPropertyRepository], logger: Type[ILogger],
                 cron: Type[ICronManager], description_generator: Type[IDescriptionGenerator]):
        self.__publisher = publisher
        self.__repository = repository
        self.__logger = logger
        self.__cron = cron
        self.__description_generator = description_generator

    async def publish(self, property: Property) -> None:
        property.description = await self.__description_generator.generate(property)
        try:
            property.description = await self.__description_generator.generate(property)
        except Exception as e:
            self.__logger.error(f"generate description for property: {property.url} error: {str(e)}")
            raise e
        try:
            await self.__publisher.add(property)
            self.__logger.info(f"property: {property.url} was published to all source")
        except Exception as e:
            self.__logger.error(f"publish property: {property.url} error: {str(e)}")
            raise e

        try:
            self.__repository.add(property)
            self.__logger.info(f"property: {property.url} was add to repository")
        except Exception as e:
            self.__logger.error(f"add to repository property {property.url} error: {str(e)}")
            self.__cron.add(property.url + datetime.datetime.now().isoformat() + "add to repo", self.__repository.add,
                            trigger='date',
                            run_date=datetime.datetime.now() + datetime.timedelta(minutes=3), args=(property,))
            raise e
