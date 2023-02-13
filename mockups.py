import asyncio
from typing import Callable, Type, Coroutine

from cron import Job
from logger import ILogger
from publisher import IPublisher
from description import IDescriptionGenerator
from description import ITranslate
from request import IChatGPTRequest
from request import IMyHomeRequest
from request import IBrowserRequest
from service import IService
from converter import ITelegramMessageConverter
from transport import ITransport
from cron import ICronManager
from repository import IPropertyRepository
from repository import IProxyRepository
from scrapper import IMyHomeScrapper
from task import IPublisherRetryOnExceptionTaskProvider
from logger import Logger
from entity import *

logger = Logger(False, "")


class PublisherMockUp(IPublisher):
    def __init__(self, name: str):
        self.name = name

    async def publish(self, property: Property) -> None:
        logger.debug(f"PUBLISH PROPERTY IN {self.name.upper()} PUBLISHER MOCKUP")


class DescriptionGeneratorMockUp(IDescriptionGenerator):

    async def generate(self, property: Property) -> Description:
        logger.debug("GENERATE DESCRIPTION MOCKUP")
        return Description(ru="Пример описания на русском", en="Example of description in english",
                           ge="აღწერილობის მაგალითი ქართულად")


class TranslateMockUp(ITranslate):
    def translate(self, en_text: str) -> Description:
        logger.debug("TRANSLATE DESCRIPTION MOCKUP")
        return Description(ru="Пример описания на русском", en="Example of description in english",
                           ge="აღწერილობის მაგალითი ქართულად")


class ChatGPTRequestMockUp(IChatGPTRequest):

    def send(self, text: str) -> str:
        logger.debug("CHAT_GPT_REQUEST MOCKUP")
        return "Example response of chatGPT"


class MyHomeRequestMockUp(IMyHomeRequest):

    async def get_auth_page(self) -> str:
        logger.debug("MYHOME GET AUTH PAGE MOCKUP")
        return open("mockup_data/auth_page.html", "r").read()

    async def auth(self, login: str, password: str, form_token: str, proxy: str = None) -> str:
        logger.debug("MYHOME AUTH MOCKUP")
        return "example token"

    async def upload_images(self, images: List[str], ip: str, proxy: str = None):
        logger.debug("MYHOME UPLOAD IMAGES MOCKUP")

    async def add_product_stamp(self, auth_token: str, proxy: str = None) -> str:
        logger.debug("MYHOME ADD MOCKUP MOCKUP")
        return "12345"


class BrowserRequestMockUp(IBrowserRequest):

    async def send(self, script: str, proxy: str = None) -> str:
        logger.debug("BROWSER REQUEST MOCKUP")
        return ""


class ServiceMockUp(IService):

    async def publish(self, property: Property) -> None:
        logger.debug("SERVICE MOCKUP")
        print(property)


class TelegramMessageConverterMockUp(ITelegramMessageConverter):

    def convert_message_to_raw_property_object(self, message: str) -> Property:
        logger.debug("TELEGRAM MESSAGE CONVERTER MOCKUP")
        return Property(url='https://www.example.com/',
                        images=["mockup_data/apartment_1.jpg", "mockup_data/apartment_2.jpg",
                                "mockup_data/apartment_3.jpg"], type='квартира', transaction_type='продажа',
                        building=Building(type='новая постройка', ceiling_height='3', house_delivery='12/2022'),
                        condition='черный каркас', usd_price=float('70000'),
                        location=Location(city='батуми', hood='старый батуми район', address='2 тупик ангиса',house_number="15"),
                        rooms=Rooms(rooms='3', bedrooms='2', bathrooms='2', living_room='1', living_room_m2='15',
                                    balcony=True, balcony_area='10'), gas=True, floor='10', floors='17',
                        optionally=None,
                        description=Description(ru="Пример описания на русском", en="Example of description in english",
                                                ge="აღწერილობის მაგალითი ქართულად"), area='70', pool=False,
                        parking='дворовая парковка', heating='центральное', hot_water='центральная система отопления',
                        information=[], agent=Agent(telegram_id='1', telegram_nickname='Dizolo', name='Ivan',
                                                    phone_number='568654121'),
                        source='myhome')

    def get_address_and_house_number(self, message: str, property: Property) -> (str, str):
        return "2 тупик ангиса","15"


class TransportMockUp(ITransport):
    def __init__(self, service: Type[IService]):
        self.service = service

    def run(self) -> None:
        logger.debug("TRANSPORT MOCKUP")
        asyncio.run(self.service.publish(TelegramMessageConverterMockUp().convert_message_to_raw_property_object("")))


class CronManagerMockUp(ICronManager):

    def add(self, task_id: any, fn: Callable, **kwargs) -> Job:
        logger.debug("CRON MANAGER ADD MOCKUP")

    def remove(self, task_id: any) -> None:
        logger.debug("CRON MANAGER REMOVE MOCKUP")

    def start(self):
        logger.debug("CRON MANAGER START MOCKUP")


class PropertyRepositoryMockUp(IPropertyRepository):
    def add(self, property: Property) -> None:
        logger.debug("PROPERTY REPOSITORY ADD MOCKUP")
        print(property)

    def get_by_agent(self, telegram_id: str) -> List[Property]:
        logger.debug("PROPERTY REPOSITORY GET BY AGENT MOCKUP")
        return [TelegramMessageConverterMockUp().convert_message_to_raw_property_object("") for item in range(10)]

    def delete(self, property_url: str) -> None:
        logger.debug("PROPERTY REPOSITORY DELETE MOCKUP")


class ProxyRepositoryMockUp(IProxyRepository):

    def get(self) -> str:
        logger.debug("PROXY GET REPOSITORY MOCKUP")
        return ""


class MyHomeScrapperMockUp(IMyHomeScrapper):

    def get_form_token(self, string_html: str) -> str:
        logger.debug("MY HOME SCRAPPER MOCKUP")
        return "Example form token"


class PublisherRetryOnExceptionTaskProviderMockUp(IPublisherRetryOnExceptionTaskProvider):

    def get_task(self, fn, retry_number: int, logger: Type[ILogger], sleep_on_exception: int, *args,
                 **kwargs) -> Coroutine:
        logger.debug("PUBLISHER RETRY ON EXCEPTION TASK PROVIDER MOCKUP")

        async def __inner():
            logger.debug("INNER FUNC")

        return __inner
