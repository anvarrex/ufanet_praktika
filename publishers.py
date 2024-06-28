import paho.mqtt.client as mqtt
from random import *
from dotenv import load_dotenv
import os
import time
from threading import Thread


topic_one = 'DEVICE/FF-FF-FF-FF-FF-FF/EVENT'
topic_two = 'DEVICE/AA-AA-AA-AA-AA-AA/EVENT'

load_dotenv()

MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))


def main():
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

    publisher_one = mqtt.Client()
    publisher_one.on_connect = on_connect

    publisher_one.connect(MQTT_BROKER, MQTT_PORT, 60)

    publisher_two = mqtt.Client()
    publisher_two.on_connect = on_connect

    publisher_two.connect(MQTT_BROKER, MQTT_PORT , 60)

    def inf_one():
        while True:
            data_p1 = 'temperature: ' + str(randint(1, 100))
            #print('Publisher 1:',topic_one, data_p1)
            wait = randint(1, 4)
            publisher_one.publish(topic_one, data_p1)
            time.sleep(wait)



    def inf_two():
        while True:
            data_p2 = 'height: ' + str(randint(100, 500))
            #print('Publisher 2:', topic_two, data_p2)
            wait = randint(1, 4)
            publisher_two.publish(topic_two, data_p2)
            time.sleep(wait)

    Thread(target=inf_one).start()
    Thread(target=inf_two).start()


main()
# Thread(target=main).start()