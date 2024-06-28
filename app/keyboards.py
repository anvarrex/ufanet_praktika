from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Добавить устройство')]
],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню')

main_two = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Добавить устройство'), KeyboardButton(text = 'Список устройств')],
    [KeyboardButton(text = 'Начать получение данных')]
],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню')

stop_info = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Добавить устройство'), KeyboardButton(text = 'Список устройств')],
    [KeyboardButton(text = 'Прекратить получение данных')]
],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню')

undo = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Отмена')]
],
                resize_keyboard=True,
                input_field_placeholder='Выберите пункт меню')

