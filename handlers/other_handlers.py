import ast
from aiogram import Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup

from key_boards.main_menu import button_send, variable_fire
from services.services import Services, AdminIdsFilter
from lexicon.lexicon import LEXICON_MESSAGE, LEXICON_MENU
from config_data.config import load_config

router: Router = Router()

config = load_config()

router.message.filter(AdminIdsFilter(config.tg_bot.admin_ids))

storage: MemoryStorage = MemoryStorage()

integers_kb = {'0', '1', '2', '3', '4'}
words_kb = {}


class FSMtime(StatesGroup):
    setTime = State()


class FSMstart_web(StatesGroup):
    setSlug = State()
    sendSlug = State()


class FSMafter_web(StatesGroup):
    setSlugs = State()
    sendSlugs = State()


@router.message(Command('set_time'), StateFilter(default_state))
async def set_time(message: Message, state: FSMContext):
    result = Services().get_time()
    await message.answer(text=LEXICON_MESSAGE['/set_time'])
    await state.set_state(FSMtime.setTime)


@router.message(Command('chanel'), StateFilter(default_state))
async def chanel_time(message: Message, state: FSMContext):
    await message.answer(text='отменять нечего')


@router.message(Command('chanel'), ~StateFilter(default_state))
async def chanel_time(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Изменение отменено')


@router.message(StateFilter(FSMtime.setTime), F.text)
async def process_waiting_message(message: Message, state: FSMContext):
    Services().set_time(ast.literal_eval(message.text))
    result = Services().get_time()
    await message.answer(text=f'Таблица изменена \n{result}')
    await state.clear()


@router.message(StateFilter(FSMtime.setTime))
async def process_waiting_message_error(message: Message, state: FSMContext):
    await message.answer(text=f'Вы точно отправили верный тип данных?')


@router.message(Command('get_time'))
async def get_time(message: Message):
    result = Services().get_time()
    await message.answer(text=f'{result}')


@router.message(Command('start_web'), StateFilter(default_state))
async def start_web(message: Message, state: FSMContext):
    await message.answer(text='Отправьте ссылку на zoom следующим сообщением')
    await state.set_state(FSMstart_web.setSlug)


@router.message(StateFilter(FSMstart_web.setSlug), F.text)
async def stop_and_nextCmd(message: Message, state: FSMContext):
    command = message.text

    if command.startswith('/'):
        if command == '/start_web':
            await message.answer(text='Команда уже активна. Вы можете отправлять ссылку.')
        elif command == '/cancel':
            await chanel_time(message)
        elif command == '/after_web':
            await after_web(message, state)
        elif command == '/get_time':
            await state.clear()
            await get_time(message)
        elif command == '/set_time':
            await state.clear()
            await set_time(message, state)
        else:
            await message.answer(text='Неизвестная команда. Попробуйте еще раз.')

    else:

        if command.startswith('https://') or command.startswith('http://'):
            await message.answer(text=f'Отправится данное сообщение \n{LEXICON_MESSAGE["/start_web"]} {command}',
                                 reply_markup=button_send(text="Отправить", key="Send"))
            await state.update_data(slug=command)
            await state.set_state(FSMstart_web.sendSlug)
        else:
            await message.answer(text='Ссылка должна начинаться на https или http')


@router.message(StateFilter(FSMstart_web.setSlug))
async def warning_not_slug(message: Message):
    await message.answer(text="Кажется вы отправили не ссылку, попробуйте еще раз")


@router.callback_query(StateFilter(FSMstart_web.sendSlug), F.data.in_(['Send']))
async def proc_other_mess(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await Services().send_message(with_slug=state_data['slug'])
    await callback.message.answer(text="Сообщение отправлено")
    await state.clear()


@router.message(StateFilter(FSMstart_web.sendSlug))
async def warning_not_slug(message: Message):
    await message.answer(text="Нажмите на кнопку, чтобы отправить сообщение")


@router.message(Command('after_web'), StateFilter(default_state))
async def after_web(message: Message, state: FSMContext):
    await message.answer(text='Отправьте ссылку на запись и последние материалы следующим сообщением')
    await state.set_state(FSMafter_web.setSlugs)


@router.message(StateFilter(FSMafter_web.setSlugs), F.text)
async def set_slug(message: Message, state: FSMContext):
    command = message.text

    if command.startswith('/'):
        if command == '/after_web':
            await message.answer(text='Команда уже активна. Вы можете отправлять ссылку.')
        elif command == '/cancel':
            await chanel_time(message)
        elif command == '/start_web':
            await start_web(message, state)
        elif command == '/get_time':
            await state.clear()
            await get_time(message)
        else:
            await message.answer(text='Неизвестная команда. Попробуйте еще раз.')

    else:

        if command.startswith('https://') or message.text.startswith('http://'):
            await message.answer(text=f'Отправится данное сообщение \n{LEXICON_MESSAGE["/after_web"]} {command}',
                                 reply_markup=button_send(text="Отправить", key="Sends"))
            await state.update_data(slug=message.text)
            await state.set_state(FSMafter_web.sendSlugs)
        else:
            await message.answer(text='Ссылка должна начинаться на https или http')


@router.message(StateFilter(FSMafter_web.setSlugs))
async def warning_not_slug(message: Message):
    await message.answer(text="Кажется вы отправили не ссылку, попробуйте еще раз")


@router.callback_query(StateFilter(FSMafter_web.sendSlugs), F.data.in_(['Sends']))
async def proc_other_mess(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    result = await Services().send_message(with_slug=state_data['slug'])
    await callback.message.answer(text="Сообщение отправлено")
    await state.clear()


@router.message(StateFilter(FSMafter_web.sendSlugs))
async def warning_not_slug(message: Message):
    await message.answer(text="Нажмите на кнопку, чтобы отправить сообщение")


@router.message(Command(commands=['set_fire_1', 'set_fire_2']), StateFilter(default_state))
async def send_welcome(message: Message):
    chat_id = Services().chat_id
    if message.text.startswith('/set_fire_1'):
        await message.bot.send_message(chat_id=chat_id, text="Сегодняшние пожелания от Recplace", reply_markup=variable_fire(1))

    else:
        await message.bot.send_message(chat_id=chat_id, text="Сегодняшние пожелания от Recplace", reply_markup=variable_fire(2))

