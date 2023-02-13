from abc import ABC
from abc import abstractmethod
from entity import *


class ITelegramMessageConverter(ABC):
    @abstractmethod
    def convert_message_to_raw_property_object(self, message: str) -> Property:
        ...

    @abstractmethod
    def get_address_and_house_number(self, message: str, property: Property) -> (str, str):
        ...


class TelegramMessageConverter(ITelegramMessageConverter):
    @staticmethod
    def __convert_field(key: str, value: str, property: Property) -> None:
        if key == "тип жилья":
            property.type = value
        if key == "ссылка":
            property.url = value
        elif key == 'тип жилья':
            property.type = value
        elif key == 'тип здания':
            property.building.type = value
        elif key == 'состояние':
            property.condition = value
        elif key == 'город':
            property.location.city = value
        elif key == 'район':
            property.location.hood = value
        elif key == 'адрес':
            property.location.address = value
        elif key == 'номер дома':
            property.location.house_number = value
        elif key == 'дата сдачи дома':
            property.building.house_delivery = value
        elif key == 'высота потолка':
            property.building.ceiling_height = value
        elif key == 'этаж':
            split = value.split("/")
            property.floor = split[0]
            property.floors = split[1]
        elif key == 'количество комнат':
            property.rooms.rooms = value
        elif key == 'количество спален':
            property.rooms.bedrooms = value
        elif key == 'количество туалетов':
            property.rooms.bathrooms = value
        elif key == 'количество залов':
            property.rooms.living_room = value
        elif key == 'площадь зала':
            property.rooms.living_room_m2 = value
        elif key == 'площадь квартиры':
            property.area = value
        elif key == 'площадь балкона':
            property.rooms.balcony_area = value
        elif key == 'парковка':
            property.parking = value
        elif key == 'отопление':
            property.heating = value
        elif key == 'горячая вода':
            property.hot_water = value
        elif key == 'источник':
            property.source = value
        elif key == 'цена':
            property.usd_price = value
        elif key == "балкон":
            property.rooms.balcony = True if value.lower() == "да" else False
        elif key == "бассейн":
            property.rooms.balcony = True if value.lower() == "да" else False
        elif key == "газифицирован":
            property.rooms.balcony = True if value.lower() == "да" else False

    def convert_message_to_raw_property_object(self, message: str) -> Property:
        property = Property.init_empty()
        d = {item.split(":")[0].lower().strip(): item.split(":")[1].lower().strip() for item in message.split("\n")}
        for key, value in d.items():
            self.__convert_field(key, value, property)
        return property

    def get_address_and_house_number(self, message: str, property: Property) -> (str, str):
        d = {item.split(":")[0].lower().strip(): item.split(":")[1].lower().strip() for item in message.split("\n")}
        return d["адрес"], d["номер дома"]
