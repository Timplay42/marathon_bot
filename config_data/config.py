from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    api_key: str
    admin_ids: list[int]


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(tg_bot=TgBot(token=env('TOKEN'),
                              api_key=env('API_KEY'),
                              admin_ids=list(map(int, env("ADMIN_IDS").split(',')))))
