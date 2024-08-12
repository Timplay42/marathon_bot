from aiogram import Bot
from aiogram.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestUser, \
    InlineKeyboardButton, InlineKeyboardMarkup

from lexicon.lexicon import LEXICON_MENU


def button():
    kb = [[KeyboardButton(text="Поделиться контактом", request_contact=True)],]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard

def button_send(text, key):
    buttons = [[InlineKeyboardButton(text=text, callback_data=key)]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def variable_fire(number):
    buttons = [[], []]

    for i in range(4):
        index = int(i % 2)
        print(index)
        buttons[index].append(InlineKeyboardButton(text='✨', callback_data=f'fire_{number}_{i}'))

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
