from typing import List
from typing import Union
from dataclasses import dataclass


@dataclass()
class LandLord:
    name: str
    phone_number: str


@dataclass(unsafe_hash=True)
class Agent:
    telegram_id: str
    telegram_nickname: str
    name: str
    phone_number: str


@dataclass(unsafe_hash=True)
class Description:
    ge: str
    ru: str
    en: str


@dataclass(unsafe_hash=True)
class Optionally:
    tv: bool
    internet: bool
    has_furniture_and_technic: bool
    telephone: bool
    conditioner: bool
    refrigerator: bool
    washing_machine: bool
    dishwasher: bool
    elevator: bool


@dataclass(unsafe_hash=True)
class Rooms:
    rooms: str
    bedrooms: str
    bathrooms: str
    living_room: str
    living_room_m2: str
    balcony: bool
    balcony_area: str


@dataclass(unsafe_hash=True)
class Building:
    type: str
    ceiling_height: str
    house_delivery: str


@dataclass(unsafe_hash=True)
class Location:
    city: str
    hood: str
    address: str
    house_number: str


@dataclass()
class Property:
    url: str
    images: List[str]
    type: str
    transaction_type: str
    building: Building
    condition: str
    usd_price: float
    location: Location
    rooms: Rooms
    gas: bool
    floor: str
    floors: str
    optionally: Optionally
    description: Description
    area: str
    pool: bool
    parking: str
    heating: str
    hot_water: str
    information: Union[List[str]]
    agent: Agent
    source: str

    @staticmethod
    def init_empty() -> 'Property':
        return Property("", [], '', '', Building('', '', ''), '', 0, Location('', '', ''),
                        Rooms('', '', '', '', '', False, ''), False, '', '', None, Description('', '', ''), '', False,
                        '', '', '', [], Agent('', '', '',''), '')
