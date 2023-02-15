from __future__ import annotations

import datetime

import aiohttp
import time
from typing import List
from typing import Type
from abc import ABC
from abc import abstractmethod

import httpx
import transliterate
from telethon import TelegramClient
import util
from entity import Property
from config import Telegram as TelegramConfig
from config import Facebook as FacebookConfig
from config import Myhome as MyHomeConfig
from config import Myhome as SsConfig
from cron import ICronManager
from logger import ILogger
from task import IPublisherRetryOnExceptionTaskProvider
from request import IMyHomeRequest
from request import IBrowserRequest
from repository import IProxyRepository
from scrapper import IMyHomeScrapper
from exception import *


class IPublisher(ABC):
    name: str

    @abstractmethod
    async def publish(self, property: Property) -> None:
        ...


class TelegramPublisher(IPublisher):
    def __init__(self, config: TelegramConfig, logger: Type[ILogger],
                 task_provider: Type[IPublisherRetryOnExceptionTaskProvider], cron: Type[ICronManager]):
        self.name = "telegram"
        self.__config = config
        self.__logger = logger
        self.__sleep_on_exception = config.sleep_on_exception_seconds
        self.__retry_on_exception_number = config.retry_on_exception_repeat_number
        self.__task_provider = task_provider
        self.__cron = cron
        self.__client = TelegramClient('publisher', int(self.__config.api_id), self.__config.api_hash)
        self.__client.start()

    @staticmethod
    def __generate_message(r: Property) -> str:
        return f"""{r.description.ru}\nСостояние: {r.condition}\nГазифицирован: {"Да" if r.gas else "Нет"}\nОтопление: {r.heating if r.heating else "Нет"}\nГорячая вода: {r.hot_water if r.hot_water else "Нет"} \n\nКонтакты для связи: \nTelegram: {r.agent.telegram_nickname} \nНомер телефона: {r.agent.phone_number}, {r.agent.name}"""

    async def publish(self, property: Property) -> None:
        if len(property.images):
            for group in self.__config.groups:
                try:
                    await self.__client.send_file(group, property.images[:10],
                                                  caption=self.__generate_message(property))
                    time.sleep(10)
                except Exception as e:
                    self.__logger.error(str(e))
                    self.__cron.add(task_id=property.url + self.name + str(group),
                                    fn=self.__task_provider.get_task(fn=self.__client.send_file,
                                                                     retry_number=self.__retry_on_exception_number,
                                                                     logger=self.__logger,
                                                                     sleep_on_exception=self.__sleep_on_exception,
                                                                     entity=group,
                                                                     file=property.images[:10],
                                                                     caption=self.__generate_message(property)),
                                    trigger='date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=5))
                    time.sleep(self.__sleep_on_exception)
        else:
            for group in self.__config.groups:
                try:
                    await self.__client.send_message(group, self.__generate_message(property))
                    time.sleep(10)
                except Exception as e:
                    self.__logger.error(str(e))
                    self.__cron.add(task_id=property.url + self.name + str(group),
                                    fn=self.__task_provider.get_task(fn=self.__client.send_message,
                                                                     retry_number=self.__retry_on_exception_number,
                                                                     logger=self.__logger,
                                                                     sleep_on_exception=self.__sleep_on_exception,
                                                                     entity=group,
                                                                     message=self.__generate_message(property)),
                                    trigger='date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=5))
                    time.sleep(self.__sleep_on_exception)


class FacebookPublisher(IPublisher):
    def __init__(self, config: FacebookConfig, logger: Type[ILogger],
                 task_provider: Type[IPublisherRetryOnExceptionTaskProvider], cron: Type[ICronManager]):
        self.name = "facebook"
        self.__groups = config.groups
        self.__app_id = config.app_id
        self.__app_secret = config.app_secret
        self.__access_token = config.access_token
        self.__sleep_on_exception = config.sleep_on_exception_seconds
        self.__retry_on_exception_number = config.retry_on_exception_repeat_number
        self.__logger = logger
        self.__cron = cron
        self.__task_provider = task_provider

    @staticmethod
    async def __post_image(group_id: str, img, auth_token: str):
        url = f"https://graph.facebook.com/{group_id}/photos?access_token=" + auth_token

        files = {
            'file': open(img, 'rb'),
        }
        data = {
            "published": False
        }
        async with httpx.AsyncClient() as session:
            response = await session.post(url, files=files, data=data)
        return response.json()

    async def __multiply_post(self, group_id: int | str, images: List[str], message: str, auth_token: str):
        imgs_id = []
        for img in images:
            post_id = await self.__post_image(group_id, img, auth_token)
            imgs_id.append(post_id['id'])

        args = dict()
        args["message"] = message
        for img_id in imgs_id:
            key = "attached_media[" + str(imgs_id.index(img_id)) + "]"
            args[key] = "{'media_fbid': '" + img_id + "'}"
        url = f"https://graph.facebook.com/{group_id}/feed?access_token=" + auth_token
        async with httpx.AsyncClient() as session:
            await session.post(url, data=args)

    @staticmethod
    def __generate_message(r: Property) -> str:
        return f"""{r.description.ru}\nСостояние: {r.condition}\nГазифицирован: {"Да" if r.gas else "Нет"}\nОтопление: {r.heating if r.heating else "Нет"}\nГорячая вода: {r.hot_water if r.hot_water else "Нет"} \n\nКонтакты для связи: \nTelegram: {r.agent.telegram_nickname} \nНомер телефона: {r.agent.phone_number}, {r.agent.name}"""

    async def publish(self, property: Property) -> None:
        for group in self.__groups:
            try:
                await self.__multiply_post(group, property.images[:10], self.__generate_message(property),
                                           self.__access_token)
                time.sleep(20)
            except Exception as e:
                self.__logger.error(f"publish to group with id: {group} error: {str(e)}")
                time.sleep(self.__sleep_on_exception)
                self.__cron.add(task_id=property.url + self.name + str(group),
                                fn=self.__task_provider.get_task(fn=self.__multiply_post,
                                                                 retry_number=self.__retry_on_exception_number,
                                                                 logger=self.__logger,
                                                                 sleep_on_exception=self.__sleep_on_exception,
                                                                 group_id=group,
                                                                 images=property.images[:10],
                                                                 message=self.__generate_message(property),
                                                                 auth_token=self.__access_token),
                                trigger='date', run_date=datetime.datetime.now() + datetime.timedelta(minutes=5))
                continue


class MyHomePublisher(IPublisher):
    def __init__(self, config: MyHomeConfig, logger: Type[ILogger], request: Type[IMyHomeRequest],
                 cron: Type[ICronManager], proxy_repository: Type[IProxyRepository],
                 task_provider: Type[IPublisherRetryOnExceptionTaskProvider], scrapper: Type[IMyHomeScrapper]):
        self.name = "myhome"
        self.__config = config
        self.__logger = logger
        self.__request = request
        self.__cron = cron
        self.__proxy_repository = proxy_repository
        self.__task_provider = task_provider
        self.__scrapper = scrapper

    @staticmethod
    def __get_property_type(propery_type: str) -> str:
        return {
            "квартира": "1",
            "дом": "0",
            "коммерческая недвижимость": "4",
            "земля": "5",
            "отель": "7"
        }[propery_type.lower()]

    @staticmethod
    def __get_transaction_type(operation_type: str) -> str:
        return {
            "продажа": "1",
            "аренда": "2",
            "ипотека": "3",
            "аренда посуточно": "4"
        }[operation_type.lower()]

    @staticmethod
    def __get_building_type(building_type: str) -> str:
        return {
            "новая постройка": "1",
            "старая постройка": "3",
            "в процесса строительства": "2"
        }[building_type.lower()]

    @staticmethod
    def __get_city(city: str) -> str:
        return {'тбилиси': 1996871, 'кутаиси': 8742174, 'рустави': 5997314, 'батуми': 8742159, 'абастумани': 457440730,
                'абаша': 33174341, 'агара': 265377360, 'адигени': 457440822, 'амбролаури': 34012095, 'анаклиа': 2633905,
                'аспиндза': 415574362, 'ленингор': 2537351, 'новый афон': 2612381, 'ахалкалаки': 33836428,
                'ахалцихе': 33728531, 'ахмета': 33836710, 'бакуриани': 311913158, 'багдати': 389644233,
                'пицунда': 2625159, 'болниси': 75732327, 'боржоми': 33728805, 'гагра': 1643098992, 'гал': 286418976,
                'гардабани': 292825343, 'гори': 9195296, 'гудаута': 2624491, 'гудаури': 540059524, 'гулрыпш': 2646065,
                'гурджаани': 74688344, 'дедоплисцкаро': 33880121, 'дманиси': 34011404, 'душети': 33880279,
                'вале': 34008861, 'вани': 389665587, 'зестафони': 6255831, 'зугдиди': 26605136, 'тетри-цкаро': 25724519,
                'телави': 61843693, 'тержола': 389636290, 'тианети': 95067936, 'казрети': 75745987, 'каспи': 25688527,
                'квайса': 169310536, 'лагодехи': 33880381, 'ланчхути': 628354549, 'лентехи': 159047970,
                'манглиси': 387157943, 'марнеули': 33728338, 'мартвили': 338167531, 'местиа': 628347610,
                'мцхета': 122131492, 'ниноцминда': 33880592, 'озургети': 8374107, 'они': 1997288, 'очамчыра': 2646014,
                'сагареджо': 26294040, 'садахло': 457068541, 'самтредия': 628351266, 'сачхере': 2024545,
                'сенаки': 30594351, 'сиони': 393023118, 'сигнахи': 289105944, 'сухум': 790323861,
                'степанцминда': 95807189, 'сурами': 33728182, 'ткибули': 292823696, 'поти': 33728068,
                'карели': 280181619, 'кеда': 218643951, 'кобулети': 8738685, 'кварели': 31970772, 'шаумяни': 457090149,
                'шуахеви': 218704706, 'чакви': 306086645, 'чохатаури': 479780417, 'чхороцку': 375727966,
                'цагери': 387172805, 'цхинвал': 2706851374, 'цаленджиха': 28357831, 'цалка': 34012533,
                'цнори': 26389317, 'цхалтубо': 291725496, 'чиатура': 291727016, 'харагаули': 223666778,
                'хашури': 274202979, 'хелвачаури': 540555081, 'хоби': 389635184, 'хони': 628349927, 'хуло': 540579150,
                'дзау': 170196329, 'джвари': 34009508, 'абашский муниципалитет': 2016164,
                'адигенский муниципалитет': 2013747, 'амбролаурский муниципалитет': 1997287,
                'аспиндзский муниципалитет': 2013749, 'автономная республика абхазия': 3572912,
                'ленингорский район': 2027320, 'ахалкалакский муниципалитет': 2013750,
                'ахалцихский муниципалитет': 2013748, 'ахметский муниципалитет': 2027328,
                'багдатский муниципалитет': 2024539, 'болнисский муниципалитет': 2014300,
                'боржомский муниципалитет': 2013752, 'гардабанский муниципалитет': 2014334,
                'горийский муниципалитет': 2025548, 'гурджаанский муниципалитет': 2027330,
                'дедоплисцкаройский муниципалитет': 2027334, 'дманисский муниципалитет': 2014299,
                'душетский муниципалитет': 2025552, 'ванский муниципалитет': 2024538,
                'зестафонский муниципалитет': 2024541, 'зугдидский муниципалитет': 2016161,
                'тетрицкаройский муниципалитет': 2014301, 'телавский муниципалитет': 2027329,
                'терджолский район': 2024542, 'тианетский муниципалитет': 2025551, 'каспский муниципалитет': 2025549,
                'лагодехский муниципалитет': 2027332, 'ланчхутский муниципалитет': 1995783,
                'лентехский муниципалитет': 1997285, 'марнеульский муниципалитет': 1997312,
                'мартвильский муниципалитет': 2016165, 'местийский муниципалитет': 2016168,
                'мцхетский муниципалитет': 2025550, 'ниноцминдский муниципалитет': 2013751,
                'озургетский муниципалитет': 1995403, 'сагареджойский муниципалитет': 2027335,
                'самтредский муниципалитет': 2024537, 'сенакский муниципалитет': 2016163,
                'сигнахский муниципалитет': 2027333, 'ткибульский муниципалитет': 2024546,
                'карельский муниципалитет': 2025547, 'кедский муниципалитет': 2009240,
                'кобулетский муниципалитет': 2009239, 'казбегский муниципалитет': 2025553,
                'кварелский муниципалитет': 2027331, 'знаурский район': 2537350, 'шуахевский муниципалитет': 2009241,
                'чохатаурский муниципалитет': 1995969, 'чхороцкуский муниципалитет': 2016166,
                'цагерский муниципалитет': 1997286, 'цхинвали': 2027318, 'цхинвальский район': 2027319,
                'цаленджихский муниципалитет': 2016167, 'цалкский муниципалитет': 2014298,
                'цхалтубский муниципалитет': 2024548, 'харагаулский район': 2024540, 'хашурский муниципалитет': 2025546,
                'хелвачаурский муниципалитет': 2009238, 'хобский муниципалитет': 2016162,
                'хулойский муниципалитет': 2009242, 'дзауский район': 2027316}[city.lower()]

    @staticmethod
    def __get_hood(city: str, hood: str):
        return {
            "тбилиси": {
                'глдани район': {'id': 687578743, 'coordinates': {'lat': '41.7981556', 'lon': '44.834797045441'}},
                'дидубе район': {'id': 687611312, 'coordinates': {'lat': '41.7522452', 'lon': '44.777130506665'}},
                'ваке район': {'id': 687586034, 'coordinates': {'lat': '41.70558605', 'lon': '44.723528901676'}},
                'исанский район': {'id': 688350922, 'coordinates': {'lat': '41.6921919', 'lon': '44.837163856355'}},
                'крцанисский район': {'id': 689701920, 'coordinates': {'lat': '41.65726255', 'lon': '44.872523058069'}},
                'мтацминда район': {'id': 689678147, 'coordinates': {'lat': '41.670969', 'lon': '44.748078624109'}},
                'надзаладеви район': {'id': 688137211, 'coordinates': {'lat': '41.7564578', 'lon': '44.827391155192'}},
                'сабуртальский район': {'id': 687602533,
                                        'coordinates': {'lat': '41.7687623', 'lon': '44.724123229951'}},
                'самгорский райогн': {'id': 688330506, 'coordinates': {'lat': '41.7006443', 'lon': '44.93829711282'}},
                'чугуретский район': {'id': 687618311, 'coordinates': {'lat': '41.71830105', 'lon': '44.822817520112'}}}

            ,
            "кутаиси": {
                'поселок авангарди': {'id': 204509374, 'coordinates': {'lat': '42.2528506', 'lon': '42.6635306162513'}},
                'поселок автокархана': {'id': 204528515, 'coordinates': {'lat': '42.2604901', 'lon': '42.639738'}},
                'поселок асатиани': {'id': 206352209, 'coordinates': {'lat': '42.2550914', 'lon': '42.6993924'}},
                'поселок агмашенебели': {'id': 206348743, 'coordinates': {'lat': '42.262134', 'lon': '42.6838187'}},
                'балахвани': {'id': 2145069828, 'coordinates': {'lat': '42.2615953', 'lon': '42.7080193'}},
                'бжолеби': {'id': 206349513, 'coordinates': {'lat': '42.2682245', 'lon': '42.6983195'}},
                'холм габашвили': {'id': 206345188, 'coordinates': {'lat': '42.2706022', 'lon': '42.6838528'}},
                'гора сакуслиа': {'id': 206349304, 'coordinates': {'lat': '42.26740205', 'lon': '42.6352147070453'}},
                'гуматеси': {'id': 2163598831, 'coordinates': {'lat': '42.3118948', 'lon': '42.7078256'}},
                'вакисубани': {'id': 204509275, 'coordinates': {'lat': '42.2355997', 'lon': '42.6759357812622'}},
                'застава': {'id': 5279555, 'coordinates': {'lat': '42.2642151', 'lon': '42.6745919'}},
                'мепесутубани': {'id': 204507826, 'coordinates': {'lat': '42.2713499', 'lon': '42.7026910867353'}},
                'мцванеквавила': {'id': 206347371, 'coordinates': {'lat': '42.27517165', 'lon': '42.7140827956213'}},
                'поселок никея': {'id': 204509276, 'coordinates': {'lat': '42.2368786', 'lon': '42.6922741'}},
                'ниноцминда': {'id': 206352104, 'coordinates': {'lat': '42.2579827', 'lon': '42.693749'}},
                'рионгеси': {'id': 6002742, 'coordinates': {'lat': '42.1985757', 'lon': '42.7130022'}},
                'сафичхиа': {'id': 2163556035, 'coordinates': {'lat': '42.269256', 'lon': '42.7143748'}},
                'сагориа': {'id': 204508541, 'coordinates': {'lat': '42.2484533', 'lon': '42.7133086'}},
                'укимериони': {'id': 206345498, 'coordinates': {'lat': '42.274778', 'lon': '42.6988303'}},
                'кроника': {'id': 206349898, 'coordinates': {'lat': '42.2652317', 'lon': '42.69361'}},
                'поселок чавчавадзе': {'id': 206348604, 'coordinates': {'lat': '42.2572276', 'lon': '42.6782633'}},
                'чома': {'id': 206393819, 'coordinates': {'lat': '42.2827303', 'lon': '42.7182709'}}}

            ,
            "батуми": {
                'аэропорт район': {'id': 776481390, 'coordinates': {'lat': '41.6143127', 'lon': '41.602490128999'}},
                'агмашенебели район': {'id': 776472116, 'coordinates': {'lat': '41.6268197', 'lon': '41.623158474965'}},
                'багратионский район': {'id': 776471185,
                                        'coordinates': {'lat': '41.63977365', 'lon': '41.637516504142'}},
                'бони-городокский район': {'id': 777654897,
                                           'coordinates': {'lat': '41.63948395', 'lon': '41.668763394976'}},
                'поселок тамар': {'id': 776734274, 'coordinates': {'lat': '41.6547888', 'lon': '41.682527951904'}},
                'кахаберийский район': {'id': 776998491,
                                        'coordinates': {'lat': '41.6138813', 'lon': '41.641635519779'}},
                'руставельский район': {'id': 776460995,
                                        'coordinates': {'lat': '41.64571005', 'lon': '41.624247551104'}},
                'старый батуми район': {'id': 776458944, 'coordinates': {'lat': '41.6503276', 'lon': '41.63666850758'}},
                'химшиашвили район': {'id': 776463102, 'coordinates': {'lat': '41.6379926', 'lon': '41.613705478307'}},
                'джавахишвили район': {'id': 776465448, 'coordinates': {'lat': '41.6322488', 'lon': '41.63056781933'}}}

        }[city.lower()][hood.lower()]

    @staticmethod
    def __get_full_address(city: str, hood: str) -> str:
        region = "Аджара" if city.lower() == "батуми" else ""
        return f"{hood.title()}, {city.title()}, {region.title()}"

    @staticmethod
    def __get_flat_condition(condition: str) -> str:
        return {
            "недавно отремонтированный": "1",
            "текущий ремонт": "4",
            "белый каркас": "7",
            "черный каркас": "8",
            "зеленый каркас": "9"
        }[condition.lower()]

    @staticmethod
    def __get_parking_type(t: str) -> str:
        return {
            "дворовая парковка": "0",
            "гараж": "1",
            "парковочное место": "2",
            "подземный паркинг": "3",
            "платная парковка": "4",
        }[t.lower()]

    @staticmethod
    def __get_pool_type(t: bool) -> str:
        return "1" if t else ""

    @staticmethod
    def __get_hot_water_type(t: str) -> str:
        return {
            "газовый обогреватель": "1",
            "бак": "2",
            "электрический нагреватель": "3",
            "природная горячая вода": "4",
            "солченый обогреватель": "5",
            "центральная система отопления": "6",
        }[t.lower()]

    @staticmethod
    def __get_warming_type(t: str) -> str:
        return {
            "центральное": "2",
            "газовое": "3",
            "электрическое": "4",
            "теплый пол": "5",
        }[t.lower()]

    async def __get_auth_token(self, proxy: str = None) -> str:
        try:
            form_token = await self.__get_form_token()
            return await self.__request.auth(self.__config.login, self.__config.password, form_token, proxy)
        except MyHomeNotFormTokenException:
            raise MyHomeAuthException()

    async def __get_form_token(self) -> str:
        response = await self.__request.get_auth_page()
        return self.__scrapper.get_form_token(response)

    async def __inner_publish(self, property: Property) -> None:
        proxy = self.__proxy_repository.get()
        auth_token = await self.__get_auth_token(proxy)
        property_id = await self.__request.add_product_stamp(auth_token, proxy)
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.myhome.ge',
            'Referer': f'https://www.myhome.ge/ru/my/addProduct/{property_id}',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'authtoken': auth_token,
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        hood_obj = self.__get_hood(property.location.city, property.location.hood)
        data = {
            "ProductTypeID": self.__get_property_type(property.type),
            "AdTypeID": self.__get_transaction_type(property.transaction_type),
            "estate_type_id": self.__get_building_type(property.building.type),
            "HouseDelivery": property.building.house_delivery,
            "ConditionID": self.__get_flat_condition(property.condition),
            "ProjectID": "1",
            "CeilingHeight": property.building.ceiling_height,
            "Keyword": self.__get_full_address(property.location.city, property.location.hood),
            "StreetAddr": property.location.house_number + ", " + property.location.address,
            "OsmID": hood_obj["id"],
            "MapLat": hood_obj["coordinates"]["lat"],
            "MapLon": hood_obj["coordinates"]["lon"],
            "MapZoom": "12",
            "CadCode": "",
            "AreaSize": property.area,
            "Floors": property.floors,
            "Floor": property.floor,
            "Rooms": property.rooms.rooms,
            "BedRooms": property.rooms.bedrooms,
            "BathRooms": property.rooms.bathrooms,
            "LivingRoom": property.rooms.living_room,
            "LivingRoomM2": property.rooms.living_room_m2,
            "LivingRoomType": "1",
            "Balcony": property.rooms.balcony,
            "BalconySize": property.rooms.balcony_area,
            "BalconyType": "1" if property.rooms.balcony else "",
            "ParkingID": self.__get_parking_type(property.parking) if self.__get_parking_type(
                property.parking) else "0",
            "PoolType": self.__get_pool_type(property.pool) if self.__get_pool_type(property.pool) else "0",
            "HotWaterID": self.__get_hot_water_type(property.hot_water),
            "WarmingID": self.__get_warming_type(property.heating),
            "Gas": "1" if property.gas else "0",
            "CommentGeo": property.description.ge,
            "CommentEng": property.description.en,
            "CommentRus": property.description.ru,
            "IP": util.get_ip_from_proxy(proxy),
            "MaklerId": "",
            "VideoUrl": "",
            "CurrencyID": "1",
            "Price": property.usd_price,
            "productPriceM2": str(int(property.usd_price) / int(property.area)),
            "ChangeInfo": "",
            "ProductOwner": transliterate.translit(property.agent.name, language_code='ru',
                                                   reversed=True).capitalize(),
            "Images[]": await self.__request.upload_images(property.images, util.get_ip_from_proxy(proxy)),
            "Phone": property.agent.phone_number,
            "phoneIsActive": "1",
            "code": "",
            "super_vip_packet": "0",
            "PromBlockVipQuantity": "1",
            "vip_plus_packet": "0",
            "vip_packet": "0",
            "color_packet": "0",
            "PromBlockColorQuantity": "1",
            "aupdate_packet": "0",
            "PromBlockAutoUpdateQuantity": "1",
            "PromBlockAutoUpdateHour": "0",
            "PayWithCard": [
                "0",
                "0"
            ],
            "PaymentMethod": [
                "balance",
                "balance"
            ],
            "draftId": property_id,
            "PrID": "",
            "IsDev": "0",
            "UserEmail": self.__config.login
        }
        async with httpx.AsyncClient() as session:
            response = await session.post('https://api.myhome.ge/ru/Mypage/AddProduct', data=data, headers=headers)
            self.__logger.info(response.text)

    async def publish(self, property: Property) -> None:
        try:
            await self.__inner_publish(property)
        except Exception as e:
            self.__logger.error(f"publish url: {property.url} error: {str(e)}")
            self.__cron.add(
                property.url + self.name,
                fn=self.__task_provider.get_task(self.__inner_publish,
                                                 self.__config.retry_on_exception_repeat_number,
                                                 self.__logger,
                                                 self.__config.sleep_on_exception_seconds,
                                                 property=property),
                trigger='date',
                run_date=datetime.datetime.now() + datetime.timedelta(minutes=15)
            )


class SSPublsher(IPublisher):
    def __init__(self, config: SsConfig, proxy_repository: Type[IProxyRepository], browser: Type[IBrowserRequest],
                 cron: Type[ICronManager], logger: Type[ILogger],
                 task_provider: Type[IPublisherRetryOnExceptionTaskProvider]):
        self.name = "ss"
        self.__config = config
        self.__proxy_repository = proxy_repository
        self.__browser = browser
        self.__cron = cron
        self.__logger = logger
        self.__task_provider = task_provider

    @staticmethod
    def __get_property_type_selector(p_type: str) -> str:
        return {
            "квартира": "#RealEstateTypeId_5",
            "дом": "#RealEstateTypeId_4",
            "коммерческая недвижимость": "#RealEstateTypeId_6",
            "земля": "#RealEstateTypeId_3",
            "отель": "#RealEstateTypeId_2"
        }[p_type.lower()]

    @staticmethod
    def __get_transaction_type_selector(o_type: str) -> str:
        return {
            "продажа": "#RealEstateDealTypeId_4",
            "аренда": "#RealEstateDealTypeId_1",
            "ипотека": "#RealEstateDealTypeId_2",
            "аренда посуточно": "#RealEstateDealTypeId_3"
        }[o_type.lower()]

    @staticmethod
    def __get_city_selector(city: str) -> str:
        return {
            'тбилиси': '#bs-select-1-0',
            'батуми': '#bs-select-1-1',
            'кутаиси': '#bs-select-1-2'
        }[city.lower()]

    @staticmethod
    def __get_rooms_quantity_selector(rooms: str):
        return {
            "1": "#room-1",
            "2": "#room-2",
            "3": "#room-3",
            "4": "#room-4",
            "5": "#room-5",
            "6": "#room-6",
            "7": "#room-7",
            "8": "#room-8",
            "9": "#room-9",
        }[str(rooms)]

    @staticmethod
    def __get_balcony_selector(b: bool) -> str:
        return {
            True: "#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.create-edit-dynamic-fileds > div.section-row.application-main-fields > div:nth-child(57) > div > div > div:nth-child(1) > label",
            False: "#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.create-edit-dynamic-fileds > div.section-row.application-main-fields > div:nth-child(57) > div > div > div:nth-child(6) > label"
        }[b]

    @staticmethod
    def __get_toilet_quantity_selector(t: str) -> str:
        return {
            "1": "#rad1_418",
            "2": "#rad1_419",
            "3": "#rad1_420",
            "4": "#rad1_421",
            "5": "#rad1_422",
        }[str(t)]

    @staticmethod
    def __get_building_type(b_type: str) -> str:
        return {
            "новая постройка": "#rad1_2",
            "старая постройка": "#rad1_453",
            "в процесса строительства": "#rad1_3"
        }[b_type.lower()]

    @staticmethod
    def __get_condition_selector(c: str) -> str:
        return {
            "недавно отремонтированный": "#rad1_16",
            "текущий ремонт": "#rad1_11",
            "белый каркас": "#rad1_9",
            "черный каркас": "#rad1_8",
            "зеленый каркас": "#rad1_35"
        }[c.lower()]

    @staticmethod
    def __get_gas_condition(gas: bool) -> str:
        return "true" if gas else "false"

    @staticmethod
    def __get_heating_condition(heating: str) -> str:
        return "true" if heating else "false"

    def __get_script(self, property: Property) -> str:
        return open("ss_script.js", "r").read() % (
            str(self.__config.email),
            str(self.__config.password),
        )

    async def publish(self, property: Property) -> None:
        script = self.__get_script(property)
        try:
            await self.__browser.send(script, self.__proxy_repository.get())
        except Exception as e:
            self.__logger.error(str(e))
            self.__cron.add(
                property.url + self.name,
                fn=self.__task_provider.get_task(self.__browser.send,
                                                 self.__config.retry_on_exception_repeat_number,
                                                 self.__logger,
                                                 self.__config.sleep_on_exception_seconds,
                                                 script=script,
                                                 proxy=self.__proxy_repository.get()),
                trigger='date',
                run_date=datetime.datetime.now() + datetime.timedelta(minutes=15)
            )


class MainPublisher:
    def __init__(self, publishers: List[Type[IPublisher]], logger: Type[ILogger]):
        self.__publishers = [{"name": p.name, "publisher": p} for p in publishers]
        self.__logger = logger

    async def add(self, property: Property) -> None:
        for publisher in self.__publishers:
            await publisher.get("publisher").publish(property)
            # try:
            #     await publisher.get("publisher").publish(property)
            # except Exception as e:
            #     self.__logger.error(f"publish with name: {publisher.get('name')} error: {str(e)}")
            #     continue
