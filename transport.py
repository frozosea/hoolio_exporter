import datetime
import os.path
import random
import asyncio
from abc import ABC
from typing import Type
from typing import List
from typing import Union
from abc import abstractmethod
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.files import JSONStorage
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
    handle_command = State()
    waiting_base_description = State()
    validate_base_description = State()
    waiting_images = State()
    waiting_neighbor_hood = State()
    waiting_address = State()
    check_data = State()
    waiting_confirm = State()


class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


class Telegram(ITransport):

    def __init__(self, token: str, service: Type[IService], config: TelegramConfig, logger: Type[ILogger],
                 validator: Type[IValidator], repository: Type[ILocationRepository],
                 converter: Type[ITelegramMessageConverter]):
        self.__bot = Bot(token=token)
        self.__dp = Dispatcher(self.__bot, storage=JSONStorage("storage.json"))
        self.__service = service
        self.__config = config
        self.__logger = logger
        self.__validator = validator
        self.__repository = repository
        self.__converter = converter

    async def start_message_handler(self, message: types.Message, state: FSMContext):
        await message.reply(
            "Этот бот сделан для выгрузки объявлений во всевозможные источники.Этот принадлежит Hoolio real estate inc. Если Вы не являетесь нашим сотдруником, пожалуйста, не пользуйтесь этим ботом")
        if not self.__check_user_access(message.from_user.id):
            await message.reply(
                "Упс! Кажется вы не имеете доступа к этому боту, пожалуйста, обратитесь к администратору!")
            return
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["Добавить новый объект"]
            keyboard.add(*buttons)
            await message.reply("Выберите команду", reply_markup=keyboard)
            await state.set_state(AddProperty.handle_command.state)

    async def handle_command(self, message: types.Message, state: FSMContext):
        if not self.__check_user_access(message.from_user.id):
            await message.reply(
                "Упс! Кажется вы не имеете доступа к этому боту, пожалуйста, обратитесь к администратору!")
            return
        if message.text == "Добавить новый объект":
            await message.reply(
                f"Здравствуйте, {self.__get_agent_name_by_id(message.from_user.id)}!. \nВведите базовое описание квартиры в следующем формате, поля обязательно должны называться именно так,информация в них так же должна быть отражена как в примере, в противном случае бот не сможет обработать Ваш запрос!\nПример базового описания отправится ниже.",
            )
            await message.reply("Ссылка: ссылка с гугл диска/срм\nТип операции: продажа/аренда/аренда посуточно/ипотека\nТип жилья: квартира/дом/коммерческая недвижимость/земля/отель\nТип здания: новая постройка/старая постройка/в процессе строительства\nСостояние: недавно отремонтированный/текущий ремонт/белый каркас/черный каркас/зеленый каркас\nДата сдачи дома: в формате month/year, например 12/2022\nЭтаж: 12/17\nВысота потолка: 3\nКоличество комнат: 3\nКоличество спален: 2\nКоличество туалетов: 2\nКоличество залов: 1\nПлощадь зала: 15\nПлощадь квартиры: 70\nБалкон: да/нет\nПлощадь балкона: 10 \nБассейн: да/нет \nПарковка: дворовая парковка/гараж/парковочное место/подземный паркинг/платная парковка \nОтопление: центральное/газовое/электрическое/теплый пол\nГорячая вода: газовый/бак/электрический/природная горячая вода/солченый обогреватель/центральная система отопления\nИсточник: myhome/ss/telegram/facebook\nЦена: 70000\nГазифицирован: да")
            await state.set_state(AddProperty.validate_base_description.state)
        else:
            await message.reply("Пожалуйста, выберите команду с поля для кнопок!")

    async def add_property_chosen(self, message: types.Message, state: FSMContext):
        if not self.__check_user_access(message.from_user.id):
            await message.reply(
                "Упс! Кажется вы не имеете доступа к этому боту, пожалуйста, обратитесь к администратору!")
            return
        await state.set_state(AddProperty.validate_base_description.state)

    async def base_description_written(self, message: types.Message, state: FSMContext):
        if not self.__validator.validate_add_new_property_message(message.text.lower()):
            await message.reply(
                "Введите описание в правильном формает, как указано выше! Бот не может обработать Ваш запрос!")
            await state.set_state(AddProperty.validate_base_description.state)
            return
        await state.update_data(base_data=message.text.lower())
        await message.reply(
            "Спасибо! Базовое описание было получено, теперь отправьте фотографии. Отправляйте фотографии в логическом порядке, потому что именно в этом порядке они буду отправлены на различные площадки")
        await state.set_state(AddProperty.waiting_images.state)

    async def images_sent(self, message: types.Message, album: List[types.Message], state: FSMContext, ):
        if not len(message.photo):
            await message.reply("Отправьте фотографии квартиры!")
            await state.set_state(AddProperty.waiting_images.state)
            return
        photos = []
        for photo in album:
            filename = f"{str(datetime.datetime.now().timestamp())}_{str(random.Random().randint(1, 100000))}_{self.__get_agent_name_by_id(message.from_user.id)}.jpg"
            await self.__bot.download_file_by_id(photo.photo[-1].file_id,
                                                 destination=f"photos/{filename}")
            photos.append(os.path.abspath(f"photos/{filename}"))
        print(photos)
        await state.update_data(photos=photos)
        await self.__bot.send_message(message.chat.id,
                                      "Фотографии были получены. Выберите район, где находится объект, используя кнопки ниже",
                                      reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                          *self.__repository.get_neighborhoods(self.__config.city)))
        await state.set_state(AddProperty.waiting_neighbor_hood.state)

    async def neighborhood_chosen(self, message: types.Message, state: FSMContext):
        neighborhoods = self.__repository.get_neighborhoods(self.__config.city)
        if message.text.lower() not in neighborhoods:
            await message.reply("Пожалуйста, выберите район используя кнопки!",
                                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                    *neighborhoods))
            await state.set_state(AddProperty.waiting_neighbor_hood.state)
            return
        await state.update_data(hood=message.text.lower())
        await message.reply(
            "Введите, пожалуйста, сообщение следующего вида:")
        await message.reply("Адрес: 2 переулок ангиса\nНомер дома: 15")
        await state.set_state(AddProperty.waiting_address.state)

    async def get_address(self, message: types.Message, state: FSMContext):
        m = message.text.lower()
        print(m)
        if not self.__validator.validate_address_message(m):
            await message.reply("Введите сообщение в правильном формате!")
            await state.set_state(AddProperty.waiting_address.state)
            return
        address, house_number = self.__converter.get_address_and_house_number(m)
        await state.update_data(address=address, house_number=house_number)
        await message.reply(
            "Сейчас ниже будет отправлено сообщение со всеми данными. Нажмите Да чтобы продолжить.",
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да"))
        await state.set_state(AddProperty.check_data.state)

    async def check_user_data_correct(self, message: types.Message, state: FSMContext):
        if message.text.lower() == "да":
            print("NOW CHECK USER DATA")
            data = await state.get_data()
            base_info = data["base_data"]
            base_info += f"\nГород: {self.__config.city}"
            base_info += f"\nРайон: {data['hood']}"
            base_info += f"\nАдрес: {data['address']}"
            base_info += f"\nНомер дома: {data['house_number']}"
            media = types.MediaGroup()
            for index, image in enumerate(data["photos"], 0):
                if index <= 9:
                    media.attach_photo(types.InputFile(image),
                                       base_info if index == 0 else "")
            await self.__bot.send_media_group(chat_id=message.chat.id, media=media)
            await state.update_data(base_data=base_info)
            await message.reply("Подвердите что все верно используя кнопки ниже",
                                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да", "Нет"))
            await state.set_state(AddProperty.waiting_confirm.state)
        else:
            await message.reply(
                "Сейчас ниже будет отправлено сообщение со всеми данными. Нажмите Да чтобы продолжить.",
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("Да"))
            await state.set_state(AddProperty.check_data.state)

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
                                       str(r_agent.phone_number))
            try:
                await self.__service.publish(raw_property)
                self.__logger.info(
                    f"property was added to agent: {r_agent.name} with telegram nickname: {r_agent.telegram_nickname}")
                await state.reset_data()
                await message.reply(f"Объект был добавлен к агенту: {r_agent.name} успешно!")
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons = ["Добавить новый объект"]
                keyboard.add(*buttons)
                await message.reply("Выберите команду", reply_markup=keyboard)
            except Exception as e:
                self.__logger.error(f"publish error:{e}")
                await message.reply(f"Произошла ошибка! {e}")
                return
        else:
            await state.reset_data()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["Добавить новый объект"]
            keyboard.add(*buttons)
            await message.reply("Выберите команду", reply_markup=keyboard)
            await state.set_state(AddProperty.handle_command.state)
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
        self.__dp.setup_middleware(AlbumMiddleware())
        self.__dp.register_message_handler(self.start_message_handler, commands=["start"], state="*")
        self.__dp.register_message_handler(self.handle_command, state=AddProperty.handle_command)
        self.__dp.register_message_handler(self.add_property_chosen, state=AddProperty.waiting_base_description)
        self.__dp.register_message_handler(self.base_description_written, state=AddProperty.validate_base_description)
        self.__dp.register_message_handler(self.images_sent, state=AddProperty.waiting_images, content_types=["photo"])
        self.__dp.register_message_handler(self.neighborhood_chosen, state=AddProperty.waiting_neighbor_hood)
        self.__dp.register_message_handler(self.get_address, state=AddProperty.waiting_address)
        self.__dp.register_message_handler(self.check_user_data_correct, state=AddProperty.check_data)
        self.__dp.register_message_handler(self.waiting_confirm, state=AddProperty.waiting_confirm)
        self.__logger.info("START TRANSPORT")
        executor.start_polling(self.__dp)
