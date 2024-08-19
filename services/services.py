import asyncio

from aiogram import Bot
from aiogram import types
from aiogram.filters import Filter
from services.http_client import BaseServiceAPI
from services.meta import SingletonMeta
from config_data.config import load_config, Config
from lexicon.lexicon import LEXICON_MESSAGE
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, date


class Services(metaclass=SingletonMeta):
    dict_time = {
        '2024-08-19': {"upper": "18:20:00", 'hour': "18:30:00"},
        '2024-08-20': {"upper": "15:08:00", 'hour': "15:09:00"},
        '2024-08-21': {"upper": "15:08:00", 'hour': "15:09:00"},
        '2024-08-22': {"upper": "15:08:00", 'hour': "15:09:00"},
        '2024-08-23': {"upper": "15:08:00", 'hour': "15:09:00"},
    }

    @classmethod
    def set_time(cls, dict_time: dict):
        new_dict = TimerScheduler().check_value_dict_time(cls.get_time(), dict_time)
        cls.dict_time = new_dict

    @classmethod
    def get_time(cls):
        return cls.dict_time

    def __init__(self, bot: Bot, chat_id: int):
        config: Config = load_config()

        self.key = config.tg_bot.api_key
        self.bot = bot
        self.chat_id = chat_id
        self.upper = 0

    async def get_base_info(self):
        with open('users.txt', 'r') as users_file:
            users = users_file.readlines()
            user_ids = [line.split('=') for line in users]
            return user_ids


    async def send_message(self, date=None, key=None, with_slug=None):
        base_info = await self.get_base_info()
        if base_info:
            for user in base_info:
                print(user)
                try:
                    if with_slug is not None:
                        await self.bot.send_message(chat_id=user[1], text=f'{LEXICON_MESSAGE["/start_web"]} {with_slug}')
                    else:
                        await self.bot.send_message(chat_id=user[1], text=LEXICON_MESSAGE[f'{date}_{key}'])
                except:
                    continue


class TimerScheduler(metaclass=SingletonMeta):
    def __init__(self, services):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.task_ids = {}
        self.services = services

    def task_ids_add(self, target_date, time_value, job_id, time_value_new=None):
        if time_value_new is None:
            self.task_ids[f'{target_date}T{time_value}'] = job_id
        else:
            del self.task_ids[f'{target_date}T{time_value}']
            self.task_ids[f'{target_date}T{time_value_new}'] = job_id
        print(self.task_ids)

    def schedule_tasks(self):
        print('task shed')
        for date, tasks in Services().dict_time.items():
            target_date = datetime.strptime(date, '%Y-%m-%d')
            target_date = target_date.strftime('%Y-%m-%d')
            for time_key, time_value in tasks.items():
                job_id = f"{date}_{time_key}"
                print(job_id)
                trigger = DateTrigger(run_date=f'{target_date}T{time_value}')
                self.scheduler.add_job(
                    self.services.send_message,
                    trigger,
                    id=job_id,
                    start_date=target_date,
                    kwargs={'date': date, 'key': time_key}
                )

                self.task_ids_add(target_date, time_value, job_id)

    def remove_tasks(self, date, time_value, time_key, time_value_new):
        print(self.task_ids)
        target_date = datetime.strptime(date, '%Y-%m-%d')
        target_date = target_date.strftime('%Y-%m-%d')
        task_ids_key = f'{target_date}T{time_value}'
        print(task_ids_key)
        if task_ids_key not in self.task_ids.keys():
            raise Exception(f'Task not found')

        self.scheduler.remove_job(self.task_ids[task_ids_key])
        job_id = f"{date}_{time_key}"
        print(job_id)
        trigger = DateTrigger(run_date=f'{target_date}T{time_value_new}')
        self.scheduler.add_job(
            self.services.send_message,
            trigger,
            id=job_id,
            start_date=target_date,
            kwargs={'date': date, 'key': time_key}
        )
        self.task_ids_add(target_date, time_value, job_id, time_value_new)

    def check_date(self, key_f, value_s, value_new):
        specified_datetime = datetime.strptime(f'{key_f} {value_s}', '%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(str(datetime.now().replace(microsecond=0)), '%Y-%m-%d %H:%M:%S')
        new = datetime.strptime(f'{key_f} {value_new}', '%Y-%m-%d %H:%M:%S')
        print(specified_datetime, now)
        return specified_datetime > now and new > now
    
    
    def check_value_dict_time(self, dict_time_old, dict_time_new):
        new_dict = {**dict_time_new}
        for key_f, value_f in dict_time_old.items():
            print(key_f, value_f)
            if value_f != dict_time_new[key_f]:
                for key_s, value_s in value_f.items():
                    if value_s != dict_time_new[key_f][key_s]:
                        check_me = self.check_date(key_f, value_s, dict_time_new[key_f][key_s])
                        if check_me:
                            print(key_f, key_s, value_s)
                            self.remove_tasks(key_f, value_s, key_s, dict_time_new[key_f][key_s])
                        else:
                            new_dict[key_f][key_s] = value_s
        return new_dict


class AdminIdsFilter(Filter):
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, message: types.Message) -> bool:
        return (message.from_user.id in self.admin_ids) and (message.chat.type not in ['group', 'supergroup'])