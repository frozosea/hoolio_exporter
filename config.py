# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome8_from_dict(json.loads(json_string))

from typing import Any, List, TypeVar, Callable, Type, cast


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


class Agent:
    telegram_id: int
    telegram_nickname: str
    name: str
    phone_number: str

    def __init__(self, telegram_id: int, telegram_nickname: str, name: str, phone_number: str) -> None:
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
        phone_number = from_str(obj.get("phone_number"))
        return Agent(telegram_id, telegram_nickname, name, phone_number)

    def to_dict(self) -> dict:
        result: dict = {}
        result["telegram_id"] = from_int(self.telegram_id)
        result["telegram_nickname"] = from_str(self.telegram_nickname)
        result["name"] = from_str(self.name)
        result["phone_number"] = from_str(self.phone_number)
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
    proxies: List[Any]
    chat_gpt_api_key: str
    telegram_bot_token: str
    cron_use_mockup: bool
    description_generator_use_mockup: bool
    proxy_repository_use_mockup: bool
    property_repository_use_mockup: bool
    transport_use_mockup: bool

    def __init__(self, base_logs_dir_name: str, upload_images_app_url: str, proxies: List[Any], chat_gpt_api_key: str, telegram_bot_token: str, cron_use_mockup: bool, description_generator_use_mockup: bool, proxy_repository_use_mockup: bool, property_repository_use_mockup: bool, transport_use_mockup: bool) -> None:
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

    @staticmethod
    def from_dict(obj: Any) -> 'BuilderConfig':
        assert isinstance(obj, dict)
        base_logs_dir_name = from_str(obj.get("base_logs_dir_name"))
        upload_images_app_url = from_str(obj.get("upload_images_app_url"))
        proxies = from_list(lambda x: x, obj.get("proxies"))
        chat_gpt_api_key = from_str(obj.get("chat_gpt_api_key"))
        telegram_bot_token = from_str(obj.get("telegram_bot_token"))
        cron_use_mockup = from_bool(obj.get("cron_use_mockup"))
        description_generator_use_mockup = from_bool(obj.get("description_generator_use_mockup"))
        proxy_repository_use_mockup = from_bool(obj.get("proxy_repository_use_mockup"))
        property_repository_use_mockup = from_bool(obj.get("property_repository_use_mockup"))
        transport_use_mockup = from_bool(obj.get("transport_use_mockup"))
        return BuilderConfig(base_logs_dir_name, upload_images_app_url, proxies, chat_gpt_api_key, telegram_bot_token, cron_use_mockup, description_generator_use_mockup, proxy_repository_use_mockup, property_repository_use_mockup, transport_use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["base_logs_dir_name"] = from_str(self.base_logs_dir_name)
        result["upload_images_app_url"] = from_str(self.upload_images_app_url)
        result["proxies"] = from_list(lambda x: x, self.proxies)
        result["chat_gpt_api_key"] = from_str(self.chat_gpt_api_key)
        result["telegram_bot_token"] = from_str(self.telegram_bot_token)
        result["cron_use_mockup"] = from_bool(self.cron_use_mockup)
        result["description_generator_use_mockup"] = from_bool(self.description_generator_use_mockup)
        result["proxy_repository_use_mockup"] = from_bool(self.proxy_repository_use_mockup)
        result["property_repository_use_mockup"] = from_bool(self.property_repository_use_mockup)
        result["transport_use_mockup"] = from_bool(self.transport_use_mockup)
        return result


class Facebook:
    access_token: str
    app_id: str
    app_secret: str
    groups: List[Any]
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool

    def __init__(self, access_token: str, app_id: str, app_secret: str, groups: List[Any], sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool) -> None:
        self.access_token = access_token
        self.app_id = app_id
        self.app_secret = app_secret
        self.groups = groups
        self.sleep_on_exception_seconds = sleep_on_exception_seconds
        self.retry_on_exception_repeat_number = retry_on_exception_repeat_number
        self.use_mockup = use_mockup

    @staticmethod
    def from_dict(obj: Any) -> 'Facebook':
        assert isinstance(obj, dict)
        access_token = from_str(obj.get("access_token"))
        app_id = from_str(obj.get("app_id"))
        app_secret = from_str(obj.get("app_secret"))
        groups = from_list(lambda x: x, obj.get("groups"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        return Facebook(access_token, app_id, app_secret, groups, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["access_token"] = from_str(self.access_token)
        result["app_id"] = from_str(self.app_id)
        result["app_secret"] = from_str(self.app_secret)
        result["groups"] = from_list(lambda x: x, self.groups)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        return result


class Myhome:
    login: str
    password: str
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool

    def __init__(self, login: str, password: str, sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool) -> None:
        self.login = login
        self.password = password
        self.sleep_on_exception_seconds = sleep_on_exception_seconds
        self.retry_on_exception_repeat_number = retry_on_exception_repeat_number
        self.use_mockup = use_mockup

    @staticmethod
    def from_dict(obj: Any) -> 'Myhome':
        assert isinstance(obj, dict)
        login = from_str(obj.get("login"))
        password = from_str(obj.get("password"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        return Myhome(login, password, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["login"] = from_str(self.login)
        result["password"] = from_str(self.password)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        return result


class Telegram:
    api_id: str
    api_hash: str
    phone_number: str
    groups: List[Any]
    sleep_on_exception_seconds: int
    retry_on_exception_repeat_number: int
    use_mockup: bool

    def __init__(self, api_id: str, api_hash: str, phone_number: str, groups: List[Any], sleep_on_exception_seconds: int, retry_on_exception_repeat_number: int, use_mockup: bool) -> None:
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
        api_id = from_str(obj.get("api_id"))
        api_hash = from_str(obj.get("api_hash"))
        phone_number = from_str(obj.get("phone_number"))
        groups = from_list(lambda x: x, obj.get("groups"))
        sleep_on_exception_seconds = from_int(obj.get("sleep_on_exception_seconds"))
        retry_on_exception_repeat_number = from_int(obj.get("retry_on_exception_repeat_number"))
        use_mockup = from_bool(obj.get("use_mockup"))
        return Telegram(api_id, api_hash, phone_number, groups, sleep_on_exception_seconds, retry_on_exception_repeat_number, use_mockup)

    def to_dict(self) -> dict:
        result: dict = {}
        result["api_id"] = from_str(self.api_id)
        result["api_hash"] = from_str(self.api_hash)
        result["phone_number"] = from_str(self.phone_number)
        result["groups"] = from_list(lambda x: x, self.groups)
        result["sleep_on_exception_seconds"] = from_int(self.sleep_on_exception_seconds)
        result["retry_on_exception_repeat_number"] = from_int(self.retry_on_exception_repeat_number)
        result["use_mockup"] = from_bool(self.use_mockup)
        return result


class Config:
    telegram: Telegram
    facebook: Facebook
    myhome: Myhome
    ss: Myhome
    agent_network: List[AgentNetwork]
    builder_config: BuilderConfig

    def __init__(self, telegram: Telegram, facebook: Facebook, myhome: Myhome, ss: Myhome, agent_network: List[AgentNetwork], builder_config: BuilderConfig) -> None:
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
        agent_network = from_list(AgentNetwork.from_dict, obj.get("agent_network"))
        builder_config = BuilderConfig.from_dict(obj.get("builder_config"))
        return Config(telegram, facebook, myhome, ss, agent_network, builder_config)

    def to_dict(self) -> dict:
        result: dict = {}
        result["telegram"] = to_class(Telegram, self.telegram)
        result["facebook"] = to_class(Facebook, self.facebook)
        result["myhome"] = to_class(Myhome, self.myhome)
        result["ss"] = to_class(Myhome, self.ss)
        result["agent_network"] = from_list(lambda x: to_class(AgentNetwork, x), self.agent_network)
        result["builder_config"] = to_class(BuilderConfig, self.builder_config)
        return result

