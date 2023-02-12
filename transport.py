import datetime
import random
from abc import ABC
from typing import Type
from abc import abstractmethod
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
from service import IService
from logger import ILogger
from config import AgentNetwork as TelegramConfig
from validator import IValidator
from repository import ILocationRepository
from converter import ITelegramMessageConverter
from entity import Agent


class ITransport(ABC):
    @abstractmethod
    def run(self) -> None:
        ...


class AddProperty(StatesGroup):
    waiting_base_description = State()
    validate_base_description = State()
    waiting_images = State()
    waiting_neighbor_hood = State()
    check_data = State()
    waiting_confirm = State()


class Telegram(ITransport):

    def __init__(self, token: str, service: Type[IService], config: TelegramConfig, logger: Type[ILogger],
                 validator: Type[IValidator], repository: Type[ILocationRepository],
                 converter: Type[ITelegramMessageConverter]):
        self.__bot = Bot(token=token)
        self.__dp = Dispatcher(self.__bot)

        self.__service = service
        self.__config = config
        self.__logger = logger
        self.__validator = validator
        self.__repository = repository
        self.__converter = converter

    async def start_message_handler(self, message: types.Message):
        await message.reply("""Этот бот сделан для выгрузки объявлений во всевозможные источники.
                                Этот принадлежит Hoolio real estate inc. Если Вы не являетесь нашим сотдруником, 
                                пожалуйста, не пользуйтесь этим ботом""")
        if not self.__check_user_access(message.from_user.id):
            await message.reply(
                "Упс! Кажется вы не имеете доступа к этому боту, пожалуйста, обратитесь к администратору!")
            return
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["Добавить новый объект"]
            keyboard.add(*buttons)
            await message.reply("Выберите команду", reply_markup=keyboard)

    async def add_property_chosen(self, message: types.Message, state: FSMContext):
        if not self.__check_user_access(message.from_user.id):
            await message.reply(
                "Упс! Кажется вы не имеете доступа к этому боту, пожалуйста, обратитесь к администратору!")
            return
        await message.reply(
            f"""Здравствуйте, {self.__get_agent_name_by_id(message.from_user.id)}!. 
                Введите базовое описание квартиры в следующем формате, поля обязательно должны называться именно так, 
                информация в них так же должна быть отражена как в примере, в противном случае бот не сможет обработать Ваш запрос! 
                Пример базового описания:`
                    Ссылка: ссылка с гугл диска/срм
                    Тип операции: продажа/аренда/аренда посуточно/ипотека
                    Тип жилья: квартира/дом/коммерческая недвижимость/земля/отель
                    Тип здания: новая постройка/старая постройка/в процессе строительства
                    Состояние: недавно отремонтированный/текущий ремонт/белый каркас/черный каркас/зеленый каркас
                    Дата сдачи дома: в формате month/year, например 12/2022
                    Этаж: 12/17
                    Высота потолка: 3
                    Количество комнат: 3
                    Количество спален: 2
                    Количество туалетов: 2
                    Количество залов: 1
                    Площадь зала: 15
                    Площадь квартиры: 70
                    Балкон: да/нет
                    Площадь балкона: 10 
                    Бассейн: да/нет 
                    Парковка: дворовая парковка/гараж/парковочное место/подземный паркинг/платная парковка 
                    Отопление: центральное/газовое/электрическое/теплый пол
                    Горячая вода: газовый/бак/электрический/природная горячая вода/солченый обогреватель/центральная система отопления
                    Источник: myhome/ss/telegram/facebook
                    Цена: 70000
                    Газифицирован: да`
                            """, parse_mode="MarkdownV2")
        await state.set_state(AddProperty.validate_base_description.state)

    async def base_description_written(self, message: types.Message, state: FSMContext):
        if not self.__validator.validate_add_new_property_message(message.text.lower()):
            await message.reply(
                "Введите описание в правильном формает, как указано выше! Бот не может обработать Ваш запрос!")
            return
        await state.update_data(base_data=message.text.lower())
        await message.reply(
            "Спасибо! Базовое описание было получено, теперь отправьте фотографии. Отправляйте фотографии в логическом порядке, потому что именно в этом порядке они буду отправлены на различные площадки")
        await state.set_state(AddProperty.waiting_images.state)

    async def images_sent(self, message: types.Message, state: FSMContext):
        if not len(message.photo):
            await message.reply("Отправьте фотографии квартиры!")
            return
        for photo in message.photo:
            filename = f"{str(datetime.datetime.now().timestamp())}_{str(random.Random.randint(1, 100000))}_{self.__get_agent_name_by_id(message.from_user.id)}.jpg"
            await self.__bot.download_file_by_id(photo.file_id,
                                                 destination=f"photos/{filename}")
            await state.update_data(photos=await state.get_data()["photos"].append(filename))
        await message.reply("Фотографии были получены. Выберите район, где находится объект, используя кнопки ниже",
                            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                *self.__repository.get_neighborhoods(self.__config.city)))
        await state.set_state(AddProperty.waiting_neighbor_hood.state)

    async def neighborhood_chosen(self, message: types.Message, state: FSMContext):
        neighborhoods = self.__repository.get_neighborhoods(self.__config.city)
        if message.text.lower() not in neighborhoods:
            await message.reply("Пожалуйста, выберите район используя кнопки!",
                                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                    *neighborhoods))
            return
        await state.update_data(hood=message.text.lower())
        await state.set_state(AddProperty.check_data.state)

    async def check_user_data_correct(self, message: types.Message, state: FSMContext):
        await message.reply(
            "Сейчас ниже будет отправлено сообщение со всеми данными. Проверьте корректность их написания. Если что то неверно - нажмите `Нет` и начните всю операцию снова.",
            parse_mode="MarkdownV2")

        data = await state.get_data()

        media = types.MediaGroup()
        index = 0
        while not index == 9:
            media.attach_photo(data["photos"][index], caption=data["base_data"] if index == 0 else "")
            index += 1

        await message.reply_media_group(media)
        await message.reply("Подвердите что все верно используя кнопки ниже",
                            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет"))
        await state.set_state(AddProperty.waiting_confirm.state)

    async def waiting_confirm(self, message: types.Message, state: FSMContext):
        if message.text.lower() not in ["да", "нет"]:
            await message.reply("Выберите ответ используя кнопки ниже!")
        if message.text.lower() == "да":
            data = await state.get_data()
            self.__logger.info(
                f"{datetime.datetime.now().isoformat()} now start to add new property to agent {self.__get_agent_name_by_id(message.from_user.id)}")
            raw_property = self.__converter.convert_message_to_raw_property_object(data["base_data"])
            raw_property.images = data["photos"]
            r_agent = self.__get_agent_by_id(message.from_user.id)
            raw_property.agent = Agent(str(r_agent.telegram_id), r_agent.telegram_nickname, r_agent.name,
                                       r_agent.phone_number)
            try:
                await self.__service.publish(raw_property)
                self.__logger.info(
                    f"property was added to agent: {r_agent.name} with telegram nickname: {r_agent.telegram_nickname}")
                await state.reset_data()
                await message.reply(f"Объект был добавлен к агенту: {r_agent.name} успешно!")
            except Exception as e:
                self.__logger.error(f"publish error:{e}")
                await message.reply(f"Произошла ошибка! {e}")
                return
        else:
            await state.reset_data()
            await state.set_state(AddProperty.waiting_base_description.state)
            return

    def __get_agent_by_id(self, id: str) -> config.Agent:
        for agent in self.__config.agents:
            if agent.telegram_id == id:
                return agent
        return None

    def __get_agent_name_by_id(self, id: str) -> str:
        for agent in self.__config.agents:
            if agent.telegram_id == id:
                return agent.name.capitalize()
        return "Агент"

    def __check_user_access(self, id: str) -> bool:
        for agent in self.__config.agents:
            if agent.telegram_id == id:
                return True
        return False

    def run(self) -> None:
        self.__dp.register_message_handler(self.start_message_handler, commands=["start"], state="*")
        self.__dp.register_message_handler(self.add_property_chosen, state=AddProperty.waiting_base_description)
        self.__dp.register_message_handler(self.base_description_written, state=AddProperty.validate_base_description)
        self.__dp.register_message_handler(self.images_sent, state=AddProperty.waiting_images)
        self.__dp.register_message_handler(self.neighborhood_chosen, state=AddProperty.waiting_neighbor_hood)
        self.__dp.register_message_handler(self.check_user_data_correct, state=AddProperty.check_data)
        self.__dp.register_message_handler(self.waiting_confirm, state=AddProperty.waiting_confirm)
        self.__logger.info("START TRANSPORT")
        executor.start_polling(self.__dp)
