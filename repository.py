import random
import sqlite3
from abc import ABC
from abc import abstractmethod
from typing import List
from entity import Agent
from entity import Property
from entity import Location
from entity import Rooms
from entity import Description


class IProxyRepository(ABC):
    @abstractmethod
    def get(self) -> str:
        ...


class ProxyRepository(IProxyRepository):
    def __init__(self, proxies: List[str]):
        self.__proxies = proxies

    def get(self) -> str:
        if len(self.__proxies):
            return self.__proxies[random.Random().randint(0, len(self.__proxies) - 1)]


class IPropertyRepository(ABC):
    @abstractmethod
    def add(self, property: Property) -> None:
        ...

    @abstractmethod
    def get_by_agent(self, telegram_id: str) -> List[Property]:
        ...

    @abstractmethod
    def delete(self, property_url: str) -> None:
        ...


class PropertyRepository(IPropertyRepository):
    def __init__(self):
        self.__con = sqlite3.connect("database.db")

    def migrate(self) -> 'PropertyRepository':
        base = open("create_tables.up.sql", "r").read().split("\n\n")
        self.__con.cursor().execute(base[0])
        self.__con.cursor().execute(base[1])
        self.__con.commit()
        return self

    def seed_data(self, agents: List[Agent]) -> 'PropertyRepository':
        for agent in agents:
            self.__con.cursor().execute("INSERT INTO Agent (name,telegram_id,phone_number) VALUES(?,?,?);",
                                        (agent.name, agent.telegram_id
                                         , agent.phone_number))
        self.__con.commit()
        return self

    def add(self, property: Property) -> None:

        self.__con.cursor().execute(
            """INSERT INTO Property(
            url, 
            type, 
            operation_type, 
            building_type, 
            condition, 
            usd_price, 
            city, 
            address, 
            bedrooms, 
            living_rooms, 
            area, 
            gas, 
            heating, 
            hot_water, 
            source, 
            agent_id, 
            ru_description,
            ge_description,
            en_description) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                property.url,
                property.type,
                property.operation_type,
                property.building.type,
                property.condition,
                float(property.usd_price),
                property.location.city,
                property.location.address,
                int(property.rooms.bedrooms),
                int(property.rooms.living_room),
                int(property.area),
                1 if property.gas else 0,
                property.heating,
                property.hot_water,
                property.source,
                self.__get_agent_id_by_telegram_id(property.agent.telegram_id),
                property.description.ru,
                property.description.ge,
                property.description.en,))
        self.__con.commit()

    def __get_agent_id_by_telegram_id(self, telegram_id: str):
        return self.__con.cursor().execute("SELECT id FROM Agent AS agent WHERE agent.telegram_id = ?",
                                           (telegram_id,)).fetchone()[0]

    def get_by_agent(self, telegram_id: str) -> List[Property]:
        raw = self.__con.cursor().execute("SELECT * FROM Property LEFT JOIN Agent AS agent ON agent.telegram_id = ?",
                                          telegram_id).fetchall()
        array = []
        for item in raw:
            print()
            array.append(Property(item[1], [], item[2], item[3], item[4], item[5], item[6],
                                  Location(city=item[7], address=item[8]),
                                  Rooms(bedrooms=item[9], living_room=item[10]), item[12], "0", "0", None,
                                  Description(ru=item[18], ge=item[19], en=item[20]), item[11], False, "0", item[14],
                                  item[15], [], None, Agent(telegram_id, "", item[21], item[22])))
        return array

    def delete(self, property_url: str) -> None:
        self.__con.cursor().execute("DELETE FROM Property WHERE url = ? ", (property_url,))
        self.__con.commit()


class ILocationRepository(ABC):
    @abstractmethod
    def get_neighborhoods(self, city: str) -> List[str]:
        ...


class LocationRepository(ILocationRepository):

    def get_neighborhoods(self, city: str) -> List[str]:
        return {
            "батуми": ["аэропорт район", "агмашенебели район", "багратионский район", "бони-городокский район",
                       "поселок тамар", "кахаберийский район", "руставельский район", "старый батуми район",
                       "химшиашвили район", "джавахишвили район"],
            "кутаиси": ['поселок авангарди', 'поселок автокархана', 'поселок асатиани', 'поселок агмашенебели',
                        'бжолеби', 'холм габашвили', 'гора сакуслиа', 'вакисубани', 'застава', 'мепесутубани',
                        'мцванеквавила', 'поселок никея', 'ниноцминда', 'рионгеси', 'сагориа', 'укимериони',
                        'кроника',
                        'поселок чавчавадзе', 'чома'],
            "тбилиси": ['глдани район', 'дидубе район', 'ваке район', 'исанский район', 'крцанисский район',
                        'мтацминда район', 'надзаладеви район', 'сабуртальский район', 'самгорский райогн',
                        'чугуретский район'],
        }[city.lower()]
