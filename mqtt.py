import paho.mqtt.client as mqtt
import serial
import threading
import time
import tkinter as tk
import math
import json
import numpy as np

MQTT_HOST = "csse4011-iot.zones.eait.uq.edu.au"
BUTTON_TOPIC = "JupiterBlueButton"
GESTURE_TOPIC = "JupiterBlueGesture"

SERIAL_PORT = "/dev/ttyACM0"
# SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
# BAUD_RATE = 9600
TIMEOUT = 1

mqttc = None

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected your subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("Unsubscribe succeeded")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")
    client.disconnect()

def on_message(client, userdata, message):
    # print(f"Distance (cm): {message.payload}")

    string_data = message.payload.decode('utf-8')  # Decode byte data to string
    # ultrasonic_data = int(string_data) / 100 # Convert string to integer
    print(string_data)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. Loop will retry connection")
    else:
        client.subscribe(BUTTON_TOPIC)

def mqtt_thread():
    global mqttc
    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe
    mqttc.on_unsubscribe = on_unsubscribe

    mqttc.connect(MQTT_HOST)
    mqttc.loop_forever()

    # mqttc.publish()

def main_thread():
    while True:
        while True:
            try:
                ser = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)

                print("Connected")
                break
            except:
                # print("Failed Connect")
                pass

        while True:
            try:
                ser.write(1)
            except:
                print("Disconnected")
                break

            time.sleep(0.1)

def main():
    mqtt_thread_id = threading.Thread(target=mqtt_thread)
    mqtt_thread_id.daemon = True
    mqtt_thread_id.start()

    main_thread_id = threading.Thread(target=main_thread)
    main_thread_id.daemon = True
    main_thread_id.start()

    # global gui
    # root = tk.Tk()
    # root.title("Grid GUI")
    # gui = GridGUI(root)

    # root.mainloop()

    while True:
        global mqttc
        mqttc.publish(GESTURE_TOPIC, "hi")
        time.sleep(5)

if __name__ == "__main__":
    main()
