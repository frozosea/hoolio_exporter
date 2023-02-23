# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome3_from_dict(json.loads(json_string))

from typing import Any, List, Optional, TypeVar, Callable, Type, cast


T = TypeVar("T")


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


class Agent:
    telegram_id: int
    telegram_nickname: str
    name: str
    phone_number: int

    def __init__(self, telegram_id: int, telegram_nickname: str, name: str, phone_number: int) -> None:
        self.telegram_id = telegram_id
        self.telegram_nickname = telegram_nickname
        self.name = name
        self.phone_number = phone_number

    @staticmethod
    def from_dict(obj: Any) -> 'Agent':
        assert isinstance(obj, dict)
        telegram_id = from_int(obj.get("telegram_id"))
        telegram_nickname = from_str(obj.get("telegram_nickname"))
        name = from_str(obj.get("name"))
        phone_number = int(from_str(obj.get("phone_number")))
        return Agent(telegram_id, telegram_nickname, name, phone_number)

    def to_dict(self) -> dict:
        result: dict = {}
        result["telegram_id"] = from_int(self.telegram_id)
        result["telegram_nickname"] = from_str(self.telegram_nickname)
        result["name"] = from_str(self.name)
        result["phone_number"] = from_str(str(self.phone_number))
        return result


class AgentNetwork:
    agents: List[Agent]
    group_chat_id: int
    fee_percent: int
    city: str

    def __init__(self, agents: List[Agent], group_chat_id: int, fee_percent: int, city: str) -> None:
        self.agents = agents
        self.group_chat_id = group_chat_id
        self.fee_percent = fee_percent
        self.city = city

    @staticmethod
    def from_dict(obj: Any) -> 'AgentNetwork':
        assert isinstance(obj, dict)
        agents = from_list(Agent.from_dict, obj.get("agents"))
        group_chat_id = from_int(obj.get("group_chat_id"))
        fee_percent = from_int(obj.get("fee_percent"))
        city = from_str(obj.get("city"))
        return AgentNetwork(agents, group_chat_id, fee_percent, city)

    def to_dict(self) -> dict:
        result: dict = {}
        result["agents"] = from_list(lambda x: to_class(Agent, x), self.agents)
        result["group_chat_id"] = from_int(self.group_chat_id)
        result["fee_percent"] = from_int(self.fee_percent)
        result["city"] = from_str(self.city)
        return result


class BuilderConfig:
    base_logs_dir_name: str
    upload_images_app_url: str
    proxies: List[str]
    chat_gpt_api_key: str
    telegram_bot_token: str
    cron_use_mockup: bool
    description_generator_use_mockup: bool
    proxy_repository_use_mockup: bool
    property_repository_use_mockup: bool
    transport_use_mockup: bool
    browser_url: str
    browser_password: str
    machine_ip: str
    use_yandex_translate: bool
    yandex_api_key: str
    yandex_folder_id: str

    def __init__(self, base_logs_dir_name: str, upload_images_app_url: str, proxies: List[str], chat_gpt_api_key: str, telegram_bot_token: str, cron_use_mockup: bool, description_generator_use_mockup: bool, proxy_repository_use_mockup: bool, property_repository_use_mockup: bool, transport_use_mockup: bool, browser_url: str, browser_password: str, machine_ip: str, use_yandex_translate: bool, yandex_api_key: str, yandex_folder_id: str) -> None:
        self.base_logs_dir_name = base_logs_dir_name
        self.upload_images_app_url = upload_images_app_url
        self.proxies = proxies
        self.chat_gpt_api_key = chat_gpt_api_key
        self.telegram_bot_token = telegram_bot_token
        self.cron_use_mockup = cron_use_mockup
        self.description_generator_use_mockup = description_generator_use_mockup
        self.proxy_repository_use_mockup = proxy_repository_use_mockup
        self.property_repository_use_mockup = property_repository_use_mockup
        self.transport_use_mockup = transport_use_mockup
        self.browser_url = browser_url
        self.browser_password = browser_password
        self.machine_ip = machine_ip
        self.use_yandex_translate = use_yandex_translate
        self.yandex_api_key = yandex_api_key
        self.yandex_folder_id = yandex_folder_id

    @staticmethod
    def from_dict(obj: Any) -> 'BuilderConfig':
        assert isinstance(obj, dict)
        base_logs_dir_name = from_str(obj.get("base_logs_dir_name"))
        upload_images_app_url = from_str(obj.get("upload_images_app_url"))
        proxies = from_list(from_str, obj.get("proxies"))
        chat_gpt_api_key = from_str(obj.get("chat_gpt_api_key"))
        telegram_bot_token = from_str(obj.get("telegram_bot_token"))
        cron_use_mockup = from_bool(obj.get("cron_use_mockup"))
        description_generator_use_mockup = from_bool(obj.get("description_generator_use_mockup"))
        proxy_repository_use_mockup = from_bool(obj.get("proxy_repository_use_mockup"))
        property_repository_use_mockup = from_bool(obj.get("property_repository_use_mockup"))
        transport_use_mockup = from_bool(obj.get("transport_use_mockup"))
        browser_url = from_str(obj.get("browser_url"))
        browser_password = from_str(obj.get("browser_password"))
        machine_ip = from_str(obj.get("machine_ip"))
        use_yandex_translate = from_bool(obj.get("use_yandex_translate"))
        yandex_api_key = from_str(obj.get("yandex_api_key"))
        yandex_folder_id = from_str(obj.get("yandex_folder_id"))
        return BuilderConfig(base_logs_dir_name, upload_images_app_url, proxies, chat_gpt_api_key, telegram_bot_token, cron_use_mockup, description_generator_use_mockup, proxy_repository_use_mockup, property_repository_use_mockup, transport_use_mockup, browser_url, browser_password, machine_ip, use_yandex_translate, yandex_api_key, yandex_folder_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["base_logs_dir_name"] = from_str(self.base_logs_dir_name)
        result["upload_images_app_url"] = from_str(self.upload_images_app_url)
        result["proxies"] = from_list(from_str, self.proxies)
        result["chat_gpt_api_key"] = from_str(self.chat_gpt_api_key)
        result["telegram_bot_token"] = from_str(self.telegram_bot_token)
        result["cron_use_mockup"] = from_bool(self.cron_use_mockup)
        result["description_generator_use_mockup"] = from_bool(self.description_generator_use_mockup)
        result["proxy_repository_use_mockup"] = from_bool(self.proxy_repository_use_mockup)
        result["property_repository_use_mockup"] = from_bool(self.property_repository_use_mockup)
        result["transport_use_mockup"] = from_bool(self.transport_use_mockup)
        result["browser_url"] = from_str(self.browser_url)
        result["browser_password"] = from_str(self.browser_password)
        result["machine_ip"] = from_str(self.machine_ip)
        result["use_yandex_translate"] = from_bool(self.use_yandex_translate)
        result["yandex_api_key"] = from_str(self.yandex_api_key)
        result["yandex_folder_id"] = from_str(self.yandex_folder_id)
        return result


class Facebook:
    email: str
    password: str
    groups: List[str]
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool

    def __init__(self, email: str, password: str, groups: List[str], sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool) -> None:
        self.email = email
        self.password = password
        self.groups = groups
        self.sleep_on_exception_seconds = sleep_on_exception_seconds
        self.retry_on_exception_repeat_number = retry_on_exception_repeat_number
        self.use_mockup = use_mockup

    @staticmethod
    def from_dict(obj: Any) -> 'Facebook':
        assert isinstance(obj, dict)
        email = from_str(obj.get("email"))
        password = from_str(obj.get("password"))
        groups = from_list(from_str, obj.get("groups"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        return Facebook(email, password, groups, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["email"] = from_str(self.email)
        result["password"] = from_str(self.password)
        result["groups"] = from_list(from_str, self.groups)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        return result


class Myhome:
    login: Optional[str]
    password: str
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool
    email: Optional[str]

    def __init__(self, login: Optional[str], password: str, sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool, email: Optional[str]) -> None:
        self.login = login
        self.password = password
        self.sleep_on_exception_seconds = sleep_on_exception_seconds
        self.retry_on_exception_repeat_number = retry_on_exception_repeat_number
        self.use_mockup = use_mockup
        self.email = email

    @staticmethod
    def from_dict(obj: Any) -> 'Myhome':
        assert isinstance(obj, dict)
        login = from_union([from_str, from_none], obj.get("login"))
        password = from_str(obj.get("password"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        email = from_union([from_str, from_none], obj.get("email"))
        return Myhome(login, password, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup, email)

    def to_dict(self) -> dict:
        result: dict = {}
        result["login"] = from_union([from_str, from_none], self.login)
        result["password"] = from_str(self.password)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        result["email"] = from_union([from_str, from_none], self.email)
        return result


class Telegram:
    api_id: int
    api_hash: str
    phone_number: str
    groups: List[int]
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool

    def __init__(self, api_id: int, api_hash: str, phone_number: str, groups: List[int], sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool) -> None:
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.groups = groups
        self.sleep_on_exception_seconds = sleep_on_exception_seconds
        self.retry_on_exception_repeat_number = retry_on_exception_repeat_number
        self.use_mockup = use_mockup

    @staticmethod
    def from_dict(obj: Any) -> 'Telegram':
        assert isinstance(obj, dict)
        api_id = int(from_str(obj.get("api_id")))
        api_hash = from_str(obj.get("api_hash"))
        phone_number = from_str(obj.get("phone_number"))
        groups = from_list(from_int, obj.get("groups"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        return Telegram(api_id, api_hash, phone_number, groups, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["api_id"] = from_str(str(self.api_id))
        result["api_hash"] = from_str(self.api_hash)
        result["phone_number"] = from_str(self.phone_number)
        result["groups"] = from_list(from_int, self.groups)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        return result


class Config:
    telegram: Telegram
    facebook: Facebook
    myhome: Myhome
    ss: Myhome
    agent_network: AgentNetwork
    builder_config: BuilderConfig

    def __init__(self, telegram: Telegram, facebook: Facebook, myhome: Myhome, ss: Myhome, agent_network: AgentNetwork, builder_config: BuilderConfig) -> None:
        self.telegram = telegram
        self.facebook = facebook
        self.myhome = myhome
        self.ss = ss
        self.agent_network = agent_network
        self.builder_config = builder_config

    @staticmethod
    def from_dict(obj: Any) -> 'Config':
        assert isinstance(obj, dict)
        telegram = Telegram.from_dict(obj.get("telegram"))
        facebook = Facebook.from_dict(obj.get("facebook"))
        myhome = Myhome.from_dict(obj.get("myhome"))
        ss = Myhome.from_dict(obj.get("ss"))
        agent_network = AgentNetwork.from_dict(obj.get("agent_network"))
        builder_config = BuilderConfig.from_dict(obj.get("builder_config"))
        return Config(telegram, facebook, myhome, ss, agent_network, builder_config)

    def to_dict(self) -> dict:
        result: dict = {}
        result["telegram"] = to_class(Telegram, self.telegram)
        result["facebook"] = to_class(Facebook, self.facebook)
        result["myhome"] = to_class(Myhome, self.myhome)
        result["ss"] = to_class(Myhome, self.ss)
        result["agent_network"] = to_class(AgentNetwork, self.agent_network)
        result["builder_config"] = to_class(BuilderConfig, self.builder_config)
        return result

