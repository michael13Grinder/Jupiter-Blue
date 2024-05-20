import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import os

import tensorflow as tf
from tensorflow import keras

import read_range_doppler_lib as rangeDopplerLib

# Initialize serial connections (adjust ports as needed)
# data_port = 'COM3'     # Replace with the actual data port
# config_port = 'COM4'   # Replace with the actual configuration port
data_port = '/dev/ttyACM1'
config_port = '/dev/ttyACM0'
data_baudrate = 921600  # Baud rate for data port
config_baudrate = 115200 # Baud rate for configuration port

# Known packet size (number of bytes per packet from the radar)
# Adjust this according to the radar's output packet size.
# For example, if each packet contains 50 pairs of (range, Doppler) values:
num_pairs = 50
packet_size = num_pairs * 2 * 4  # 2 floats (range and Doppler) * 4 bytes per float

data_serial, config_serial = rangeDopplerLib.init_serial_connections(data_port, config_port, data_baudrate, config_baudrate)

if data_serial is None or config_serial is None:
    print("Failed to initialize serial connections. Exiting.")
    quit()

model = keras.models.load_model('trained_model.keras')
max_frames = 15
gesture_list = ['idle', 'left', 'right', 'up', 'down']

accumulate_data = []
while True:
    try:
        
        data = rangeDopplerLib.read_radar_data(data_serial, packet_size)
        ranges, dopplers = rangeDopplerLib.process_radar_data(data)
        if ranges.size == 50 and dopplers.size == 50:
            rangeDoppler = np.append(ranges, dopplers)
        else:
            rangeDoppler = None
            
        if isinstance(rangeDoppler, np.ndarray):
            accumulate_data.append(rangeDoppler.tolist())
            while len(accumulate_data) > max_frames:
                accumulate_data.pop(0)
            if len(accumulate_data) == max_frames:
                predictions = model.predict(np.array([accumulate_data,]))
                predictions = gesture_list[np.argmax(predictions[0])]
                if predictions != 'idle':
                    print('Prediction: ', predictions)
        time.sleep(0.03)

    except KeyboardInterrupt:
        print("Stopped by User")
        data_serial.close()
        config_serial.close()
        break
        
    





