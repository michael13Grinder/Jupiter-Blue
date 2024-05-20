import paho.mqtt.client as mqtt
import serial
import threading
import time
import tkinter as tk
import math
import json
import numpy as np
import tensorflow
from tensorflow import keras
import read_range_doppler_lib as rangeDopplerLib
import pyautogui

MQTT_HOST = "csse4011-iot.zones.eait.uq.edu.au"
BUTTON_TOPIC = "JupiterBlueButton"
GESTURE_SHOW_TOPIC = "JupiterBlueGestureShow"

START_MESSAGE = "Start"
STOP_MESSAGE = "Stop"
SECOND_30_MESSAGE = "30 Seconds"


GESTURE_LIST = ['idle', 'left', 'right', 'volumeup', 'volumedown']
GESTURE_FRAMES = 15

SERIAL_PORT = "/dev/ttyACM0"
# SERIAL_PORT = 'COM6'
BAUD_RATE = 115200
# BAUD_RATE = 9600
TIMEOUT = 1

RADAR_DATA_PORT = '/dev/ttyACM1'
RADAR_CONFIG_PORT = '/dev/ttyACM0'
RADAR_DATA_BAUDRATE = 921600  # Baud rate for data port
RADAR_CONFIG_BAUDRATE = 115200 # Baud rate for configuration port

mqttc = None

radar_status = 0

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
    # global string_data
    # string_data = message.payload.decode('utf-8')  # Decode byte data to string
    # ultrasonic_data = int(string_data) / 100 # Convert string to integer
    # print(string_data)
    message = message.payload.decode('utf-8')
    global radar_status
    if message == START_MESSAGE:
        radar_status = 1
    elif message == STOP_MESSAGE:
        radar_status = 0

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

def serial_thread():
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
            data_str = ""
            while True:
                try:
                    byte = ser.read()  # Read one byte at a time
                    if byte:
                        # Append the byte to the string
                        # print(byte)
                        data_str += byte.decode('utf-8')  # Assuming UTF-8 encoding
                        # Check if the entire JSON string has been received
                        if data_str.endswith('}'):
                            break  # Exit the loop once the JSON string is complete
                except:
                    print("Disconnected")
                    break
            
            print("Received:", data_str)

            # Parse JSON string into a Python dictionary
            data = json.loads(data_str)


            # Accessing values from the dictionary
            node = data['node']
            x_coordinate = data['x']
            y_coordinate = data['y']
            rssi_value = data['rssi']


            time.sleep(0.1)

def main():
    mqtt_thread_id = threading.Thread(target=mqtt_thread)
    mqtt_thread_id.daemon = True
    mqtt_thread_id.start()

    serial_thread_id = threading.Thread(target=serial_thread)
    serial_thread_id.daemon = True
    serial_thread_id.start()

    global mqttc
    last_action = 'idle'

    # Known packet size (number of bytes per packet from the radar)
    # Adjust this according to the radar's output packet size.
    # For example, if each packet contains 50 pairs of (range, Doppler) values:
    num_pairs = 50
    packet_size = num_pairs * 2 * 4  # 2 floats (range and Doppler) * 4 bytes per float

    data_serial, config_serial = rangeDopplerLib.init_serial_connections(RADAR_DATA_PORT, RADAR_CONFIG_PORT, RADAR_DATA_BAUDRATE, RADAR_CONFIG_BAUDRATE)
    if data_serial is None or config_serial is None:
        print("Failed to initialize serial connections. Exiting.")
        quit()

    model = keras.models.load_model('trained_model.keras')

    accumulate_data = []

    while True:
        try:
            if radar_status == 1:
                data = rangeDopplerLib.read_radar_data(data_serial, packet_size)
                ranges, dopplers = rangeDopplerLib.process_radar_data(data)
                if ranges.size == 50 and dopplers.size == 50:
                    rangeDoppler = np.append(ranges, dopplers)
                else:
                    rangeDoppler = None
                    
                if isinstance(rangeDoppler, np.ndarray):
                    accumulate_data.append(rangeDoppler.tolist())
                    while len(accumulate_data) > GESTURE_FRAMES:
                        accumulate_data.pop(0)
                    if len(accumulate_data) == GESTURE_FRAMES:
                        predictions = model.predict(np.array([accumulate_data,]))
                        predictions = GESTURE_LIST[np.argmax(predictions[0])]
                        if predictions != last_action and (time.time() - last_send) >= 1:
                            print(predictions)
                            last_action == predictions
                            last_send = time.time()
                            pyautogui.press(predictions)
                            mqttc.publish(GESTURE_SHOW_TOPIC, predictions.upper())                    
            time.sleep(0.03)
            
        # Stop the program and close everything if Ctrl + c is pressed
        except KeyboardInterrupt:
            print("Stopped by User")
            data_serial.close()
            config_serial.close()
            break              

if __name__ == "__main__":
    main()
