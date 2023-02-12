import re
from abc import ABC
from abc import abstractmethod


class IValidator(ABC):
    @abstractmethod
    def validate_add_new_property_message(self, message: str) -> bool:
        ...


class Validator(IValidator):
    @staticmethod
    def __validate_by_regex(pattern: str, string: str) -> bool:
        return not len(re.findall(pattern, string)) == 0

    def validate_add_new_property_message(self, message: str) -> bool:
        d = {item.split(":")[0].lower().strip(): item.split(":")[1].lower().strip() for item in message.split("\n")}
        for item in ['тип операции', 'тип жилья', 'тип здания', 'дата сдачи дома', 'высота потолка',
                     'количество комнат',
                     'количество спален', 'количество туалетов', 'количество залов', 'площадь квартиры', 'балкон',
                     'отопление', 'горячая вода', 'источник', 'цена', 'газифицирован', 'состояние', 'этаж'
                     ]:
            if not item in d.keys():
                return False
        if d["тип операции"] not in ["продажа", "аренда", "аренда посуточно", "ипотека"]:
            return False
        if d["тип жилья"] not in ['квартира', 'дом', 'коммерческая недвижимость', 'земля', 'отель']:
            return False
        if d["тип здания"] not in ['новая постройка', 'старая постройка', 'в процессе строительства']:
            return False
        if d["состояние"] not in ['недавно отремонтированный', 'текущий ремонт', 'белый каркас', 'черный каркас',
                                  'зеленый каркас']:
            return False
        if not len(re.findall(r"\d{2}/\d{4}", d["дата сдачи дома"])):
            return False
        if not d["высота потолка"].isdigit():
            return False
        if not d["количество комнат"].isdigit():
            return False
        if not d["количество спален"].isdigit():
            return False
        if not d["количество туалетов"].isdigit():
            return False
        if not d["количество залов"].isdigit():
            return False
        if not d["площадь квартиры"].isdigit():
            return False
        if d["площадь зала"]:
            if not d["площадь зала"].isdigit():
                return False
        if d["парковка"]:
            if d["парковка"] not in ['дворовая парковка', 'гараж', 'парковочное место', 'подземный паркинг',
                                     'платная парковка']:
                return False
        if d["отопление"] not in ['центральное', 'газовое', 'электрическое', 'теплый пол']:
            return False
        if d["горячая вода"] not in ['газовый', 'бак', 'электрический', 'природная горячая вода',
                                     'солченый обогреватель', 'центральная система отопления']:
            return False
        if d["балкон"] not in ["да", "нет"]:
            return False
        if d["источник"] not in ['myhome', 'ss', 'telegram', 'facebook']:
            return False
        if not d["цена"].isdigit():
            return False
        if d["газифицирован"] not in ["да", "нет"]:
            return False
        if not len(re.findall(r"\d{1,2}\/\d{1,2}", d["этаж"])):
            return False
        if not d["ссылка"]:
            return False
        return True
