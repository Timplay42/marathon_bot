import ast
import json
import logging
from http import HTTPStatus
from http.client import HTTPException

from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import BufferedInputFile, Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter

from services.http_client import BaseServiceAPI
from services.services import Services
from key_boards.main_menu import button
from config_data.config import Config, load_config
from lexicon.lexicon import LEXICON_MESSAGE, LEXICON_MENU

config: Config = load_config()

router: Router = Router()



@router.message(Command("start"), StateFilter("*"))
async def start(message: Message, command: CommandObject):
    user_id = command.args

    if user_id and user_id.startswith('user_id'):
        user_id = user_id.replace('user_id-', '')


    if user_id:
        base_info = await Services().get_base_info()

        check_user_id = False
        check_telegram_id = False
        for user in base_info:
            if str(user_id) == user[0]:
                check_user_id = True
                if str(message.from_user.id) + '\n' == user[1]:
                    check_telegram_id = True

        if check_user_id and check_telegram_id:
            await message.answer('Вы уже зарегестрированы')
            return

        elif check_user_id and not check_telegram_id:
            await message.answer('Вы не владелец данной ссылки')
            return

        elif not check_user_id and check_telegram_id:
            print(check_user_id, check_telegram_id)
            await message.answer("У вас другая ссылка для регистрации")
            return

        else:
            url = f'https://dev.recplace.ru/api/v1/bots_marathon/user/{user_id}'
            headers = {
                'accept': 'application/json',
                'API-Key': f'{config.tg_bot.api_key}',
                'Content-Type': 'application/json'
            }
            user_access = await BaseServiceAPI().get(url=url, add_headers=headers)
            if "Internal Server Error" not in user_access:
                if isinstance(user_access, dict) and len(user_access['subscription']) != 0:
                    for user_acces in user_access['subscription']:
                        if user_acces['name'] == 'Подписка GeoRecplace':
                            with open('users.txt', 'a') as f:
                                f.write(f"{user_id}={message.from_user.id}\n")
                            await message.bot.send_photo(chat_id=message.chat.id, photo='AgACAgIAAxkBAAICc2a2Ow5ZKrdToVMJ-mYoedo4kVsbAAKJ3zEbR8m5SSXePQI4fl2VAQADAgADeQADNQQ', caption=LEXICON_MESSAGE['/start'])
                            return

                else:
                    await message.answer("У вас нету доступа к марафону, извините")
                    return
            else:
                await message.answer("Проверьте правильность вставленной ссылки")
                return
    else:
        await message.answer("Перейдите по ссылке, которую вы получили после оплаты и тогда у вас получится зарегестрироваться")
        return


@router.message(Command('help'))
async def proc_statr_command(message: Message):
    await message.answer(LEXICON_MESSAGE['/help'])


@router.message()
async def other_message(message: Message):
    await message.answer("Этот бот предназначен для напоминания о трансляциях и выдаче полезный материалов")


@router.callback_query(lambda c: c.data.startswith('fire_'))
async def process_callback(callback: CallbackQuery):
    await callback.answer(LEXICON_MENU[callback.data], show_alert=True)
