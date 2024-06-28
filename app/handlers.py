import logging
import time
import os

from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F, Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import asyncio
from threading import Thread


from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from run import bot

import app.keyboards as kb
import paho.mqtt.client as mqtt

from publishers import topic_one as tpc1
from publishers import topic_two as tpc2

from dotenv import load_dotenv, find_dotenv
class add_dev(StatesGroup):
    tpc = State()

class further(StatesGroup):
    act = State()


class delete_dev(StatesGroup):
    device = State()

topics = [tpc1,
          tpc2]

print(topics)

#подписки пользователя
subscriptions = {}

#сообщения которые должен получить пользователь подписавшись на определенный топик
msgs = {}

#флажок отправки сообщения пользователю
msgs_send_to_user={}

#обработанные сообщения после удаления устройства
msgs_after_delete = {}

router = Router()

#отправленные сообщения пользователю
sentmsg = {}

load_dotenv(find_dotenv())

MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
print(MQTT_BROKER)
print(MQTT_PORT)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    tpc = msg.topic
    msg = msg.payload.decode()
    print("Received message: " + tpc + " " + msg)
    for user in subscriptions:
        for topic in subscriptions[user]:
            if tpc == topic:
                print('msgs_send_to_user', msgs_send_to_user)
                msgs[user].append('*Сообщение от ' + tpc[7:24] + '*\n' + msg)
                print('msgs', msgs)
                print('subscriptions', subscriptions)
    print('msgs_send_to_user', msgs_send_to_user)


subscriber = mqtt.Client()

subscriber.connect(MQTT_BROKER, MQTT_PORT, 60)


subscriber.on_message = on_message
subscriber.on_connect = on_connect
subscriber.loop_start()



@router.message(Command('start', 'help'))
async def cmd_start(message: Message):
    await message.answer(f'Привет, {message.from_user.username}! \n\nЭтот бот создан для прослушивания сообщений из топиков вида '
                         '/DEVICE/<mac>/EVENT и отправки сообщений пользователю, который подписался на определенный '
                         '<mac>. \n\nПожалуйста, добавьте устройство :)', reply_markup=kb.main)



@router.message(F.text == 'Добавить устройство')
async def add_device_one(message: Message, state: FSMContext):
    await state.set_state(add_dev.tpc)

    user_id = message.from_user.id

    if user_id not in subscriptions:
        subscriptions[user_id] = []
        msgs[user_id] = []
        msgs_send_to_user[user_id] = False


    await message.answer('Введите mac-адрес, на который хотите подписаться:\n'
                         '(DEVICE/<mac>/EVENT)', reply_markup=kb.undo)

@router.message(F.text == 'Отмена')
async def undo_one(message: Message, state: FSMContext):

    await state.set_state(further.act)

    user_id = message.from_user.id

    if subscriptions[user_id]:
        if not msgs_send_to_user[user_id]:
            await message.answer('Воспользуйтесь кнопками ниже для дальнейших действий :)', reply_markup=kb.main_two)
        else:
            await message.answer('Воспользуйтесь кнопками ниже для дальнейших действий :)', reply_markup=kb.stop_info)
    else:
        await message.answer('Воспользуйтесь кнопками ниже для дальнейших действий :)', reply_markup=kb.main)
    await state.clear()




@router.message(add_dev.tpc)
async def add_device_two(message: Message, state: FSMContext):

    user_id = message.from_user.id


    await state.update_data(tpc = 'DEVICE/'+message.text+'/EVENT')

    mac = 'DEVICE/'+message.text+'/EVENT'

    if mac not in subscriptions[user_id]:
        if mac in topics:
            data = await state.get_data()

            if msgs_send_to_user[user_id]:
                await message.answer(f'Отлично! Вы подписались на топик:\n{data["tpc"]}', reply_markup=kb.stop_info)
            else:
                await message.answer(f'Отлично! Вы подписались на топик:\n{data["tpc"]}', reply_markup=kb.main_two)

            subscriptions[user_id].append(str(data['tpc']))

            subscriber.subscribe(str(data['tpc']))

            print('subscriptions', subscriptions)



            await state.clear()


        else:
            await message.answer('Неверный mac-адрес! Попробуйте ещё раз.', reply_markup=kb.undo)

    else:
        await message.reply('Вы уже подключились к данному mac-адресу! Введите другой.', reply_markup=kb.undo)





@router.message(F.text == 'Начать получение данных')
async def start_getting_info(message: Message):
    user_id = message.from_user.id
    msgs_send_to_user[user_id] = True
    sentmsg[user_id] = []
    await message.answer('Пожалуйста, ожидайте :)', reply_markup=kb.stop_info)

    while msgs_send_to_user[user_id]:

        await asyncio.sleep(3)

        if not subscriptions[user_id]:
            msgs_send_to_user[user_id] = False

        try:
            print('msgs', msgs)
            if msgs_send_to_user[user_id]:
                sentmsg[user_id] = list(msgs[user_id])
                await bot.send_message(chat_id=user_id, text='\n\n'.join(sentmsg[user_id]), parse_mode="Markdown")
                while sentmsg[user_id]:

                    msgs[user_id].remove(sentmsg[user_id][0])
                    sentmsg[user_id].pop(0)

        except: pass

@router.message(F.text == 'Прекратить получение данных')
async def start_getting_info(message: Message):
    user_id = message.from_user.id
    msgs_send_to_user[user_id] = False
    await message.answer('Получение данных прекращено!', reply_markup=kb.main_two)





@router.message(F.text == 'Список устройств')
async def device_list(message: Message, state: FSMContext):
    await  state.set_state(delete_dev.device)

    user_id = message.from_user.id



    subscriptions[user_id].append('Отмена')
    print('subscriptions', subscriptions)
    device_list_kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Удалить '+ tpc[7:24])] if len(tpc)>6 else [KeyboardButton(text=tpc)] for tpc in subscriptions[user_id]
    ],
        resize_keyboard=True,
        input_field_placeholder='Нажмите на устройство, чтобы удалить его')

    await message.answer('Ваш список устройств отобразился на панели :) \nНажмите на устройство, чтобы удалить его', reply_markup=device_list_kb)

    subscriptions[user_id].remove('Отмена')


@router.message(delete_dev.device)
async def device_list_two(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(device='DEVICE/'+message.text[8:]+'/EVENT')
    data = await state.get_data()
    subscriptions[user_id].remove(data["device"])



    if subscriptions[user_id]:
        if not msgs_send_to_user[user_id]:
            await message.answer(f'Устройство {data["device"][7:24]} удалено!', reply_markup=kb.main_two)
        else:
            await message.answer(f'Устройство {data["device"][7:24]} удалено!', reply_markup=kb.stop_info)
    else:
        await message.answer(f'Устройство {data["device"][7:24]} удалено!', reply_markup=kb.main)

    tpc1_kol = 0
    tpc2_kol = 0
    for user, tpcs in subscriptions.items():
        for tpc in tpcs:
            if tpc == tpc1:
                tpc1_kol += 1
            if tpc == tpc2:
                tpc2_kol += 1
    print('tpc1', tpc1_kol)
    print('tpc2', tpc2_kol)
    if tpc1_kol == 0:
        subscriber.unsubscribe(tpc1)
    if tpc2_kol == 0:
        subscriber.unsubscribe(tpc2)



    msgs_after_delete[user_id] = list(msgs[user_id])


    for msg in msgs[user_id]:

        if data["device"][7:9] == msg[14:16]:
            msgs_after_delete[user_id].remove(msg)


    msgs[user_id] = msgs_after_delete[user_id]
    msgs_after_delete[user_id] = []



    await state.clear()

@router.message()
async def info(message: Message):
    await message.answer('Упс, похоже, что это неизвестная команда!')


