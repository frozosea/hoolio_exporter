import os
import json
from typing import Type
from typing import List
from cron import ICronManager
from cron import CronManager
from request import ChatGPTRequest
from description import IDescriptionGenerator
from description import ChatGPTTranslate
from description import YandexTranslate
from description import DescriptionGenerator
from request import IBrowserRequest
from request import BrowserRequest
from request import MyhomeRequest
from request import FacebookRequest
from scrapper import MyHomeScrapper
from logger import ILogger
from logger import Logger as CustomLogger
from config import Config
from exception import NoConfigError
from task import IPublisherRetryOnExceptionTaskProvider
from task import PublisherRetryOnExceptionTaskProvider
from repository import ILocationRepository, LocationRepository
from repository import IProxyRepository, ProxyRepository
from repository import IPropertyRepository, PropertyRepository
from publisher import IPublisher
from publisher import TelegramPublisher
from publisher import FacebookPublisher
from publisher import MyHomePublisher
from publisher import SSPublsher
from publisher import MainPublisher
from service import Service
from mockups import ProxyRepositoryMockUp
from mockups import PropertyRepositoryMockUp
from mockups import CronManagerMockUp
from mockups import PublisherMockUp
from mockups import DescriptionGeneratorMockUp
from mockups import TransportMockUp
from transport import ITransport
from transport import Telegram as TelegramTransport
from validator import Validator
from converter import TelegramMessageConverter


class Builder:
    __config: Config
    _cron: Type[ICronManager]
    _task_provider_for_publisher: Type[IPublisherRetryOnExceptionTaskProvider]
    _proxy_repository: Type[IProxyRepository]
    _location_repository: Type[ILocationRepository]
    _property_repository: Type[IPropertyRepository]
    _description_generator: Type[IDescriptionGenerator]
    _browser_request: Type[IBrowserRequest]
    _telegram_publisher: IPublisher
    _facebook_publisher: IPublisher
    _myhome_publisher: IPublisher
    _ss_publisher: IPublisher
    _publishers: List[IPublisher]
    _main_publisher: MainPublisher
    _service: Service
    _transport: Type[ITransport]

    def __init__(self):
        if not os.path.exists("config.json"):
            raise NoConfigError()
        self.__config = Config.from_dict(json.loads(open("config.json", "r").read()))
        self._publishers = []

    def __configure_cron(self, ):
        if self.__config.builder_config.cron_use_mockup:
            self._cron = CronManagerMockUp()
        else:
            self._cron = CronManager()

    def _configure_task_provider_for_publisher(self):
        self._task_provider_for_publisher = PublisherRetryOnExceptionTaskProvider()

    def __configure_logger_by_dir_name(self, dir_name) -> Type[ILogger]:
        return CustomLogger(True,
                            f"{self.__config.builder_config.base_logs_dir_name}{os.path.sep}{dir_name}")

    def __configure_repositories(self):
        if self.__config.builder_config.proxy_repository_use_mockup:
            self._proxy_repository = ProxyRepositoryMockUp()
        else:
            self._proxy_repository = ProxyRepository(self.__config.builder_config.proxies)
        self._location_repository = LocationRepository()
        if self.__config.builder_config.property_repository_use_mockup:
            self._property_repository = PropertyRepositoryMockUp()
        else:
            self._property_repository = PropertyRepository().migrate()
            self._property_repository.seed_data(self.__config.agent_network.agents)

    def __configure_description_generator(self):
        request = ChatGPTRequest(self.__config.builder_config.chat_gpt_api_key)


        if self.__config.builder_config.use_yandex_translate:
            translate = YandexTranslate(self.__config.builder_config.yandex_api_key,
                                        self.__config.builder_config.yandex_folder_id)
        else:
            translate = ChatGPTTranslate(request)


        if self.__config.builder_config.description_generator_use_mockup:
            self._description_generator = DescriptionGeneratorMockUp()
        else:
            self._description_generator = DescriptionGenerator(
                request,
                translate
            )

    def __configure_browser_request(self):
        self._browser_request = BrowserRequest(
            self.__config.builder_config.browser_url,
            self.__config.builder_config.browser_password,
            self.__config.builder_config.machine_ip,
        )

    def __configure_telegram_publisher(self):
        if self.__config.telegram.use_mockup:
            self._telegram_publisher = PublisherMockUp("telegram")
        else:
            self._telegram_publisher = TelegramPublisher(
                self.__config.telegram,
                self.__configure_logger_by_dir_name('telegram_publisher'),
                self._task_provider_for_publisher,
                self._cron
            )
        self._publishers.append(self._telegram_publisher)

    def __configure_facebook_publisher(self):
        if self.__config.facebook.use_mockup:
            self._facebook_publisher = PublisherMockUp("facebook")
        else:
            self._facebook_publisher = FacebookPublisher(
                self.__config.facebook,
                self.__configure_logger_by_dir_name("facebook_publisher"),
                FacebookRequest(
                    self.__config.facebook.email,
                    self.__config.facebook.password
                ),
                self._task_provider_for_publisher,
                self._cron
            )
        self._publishers.append(self._facebook_publisher)

    def __configure_myhome_publisher(self):
        if self.__config.myhome.use_mockup:
            self._myhome_publisher = PublisherMockUp("myhome")
        else:
            self._myhome_publisher = MyHomePublisher(
                self.__config.myhome,
                self.__configure_logger_by_dir_name("myhome_publisher"),
                MyhomeRequest(self.__config.builder_config.upload_images_app_url),
                self._cron,
                self._proxy_repository,
                self._task_provider_for_publisher,
                MyHomeScrapper()
            )
        self._publishers.append(self._myhome_publisher)

    def __configure_ss_publisher(self):
        if self.__config.ss.use_mockup:
            self._ss_publisher = PublisherMockUp("ss")
        else:
            self._ss_publisher = SSPublsher(
                self.__config.ss,
                self._proxy_repository,
                self._browser_request,
                self._cron,
                self.__configure_logger_by_dir_name("ss_publisher"),
                self._task_provider_for_publisher
            )
        self._publishers.append(self._ss_publisher)

    def __configure_main_publisher(self):
        self._main_publisher = MainPublisher(
            self._publishers,
            self.__configure_logger_by_dir_name("main_publisher")
        )

    def __configure_service(self):
        self._service = Service(
            self._main_publisher,
            self._property_repository,
            self.__configure_logger_by_dir_name("service"),
            self._cron,
            self._description_generator
        )

    def __configure_transport(self):
        if self.__config.builder_config.transport_use_mockup:
            self._transport = TransportMockUp(self._service)
        else:
            self._transport = TelegramTransport(
                self.__config.builder_config.telegram_bot_token,
                self._service,
                self.__config.agent_network,
                self.__configure_logger_by_dir_name("telegram_transport"),
                Validator(),
                self._location_repository,
                TelegramMessageConverter()
            )

    def configure(self) -> Type[ITransport]:
        self.__configure_cron()
        self._configure_task_provider_for_publisher()
        self.__configure_repositories()
        self.__configure_description_generator()
        self.__configure_browser_request()
        self.__configure_telegram_publisher()
        self.__configure_facebook_publisher()
        self.__configure_myhome_publisher()
        self.__configure_ss_publisher()
        self.__configure_main_publisher()
        self.__configure_service()
        self.__configure_transport()
        return self._transport
