import threading
import time
import sys
sys.path.insert(1, 'AWR1843-Read-Data-Python-MMWAVE-SDK-3--master')
import readData_AWR1843
import numpy as np

import tensorflow as tf
from tensorflow import keras

model = keras.models.load_model('trained_model.keras')
number_input = 150
class_names = ['none', 'left', 'right', 'up', 'down']

thread1 = threading.Thread(target=readData_AWR1843.main)
thread1.start()

time.sleep(2)

mmW_data_accumulated = [0] * number_input

mmW_data = None
while True:
    try:
        while (mmW_data is None):
            mmW_data = readData_AWR1843.get_data()
        velocity = [0.0] * (10 - len(mmW_data['velocity']))
        for i in mmW_data['velocity']:
            velocity.append(i)
        for i in velocity:
            while len(mmW_data_accumulated) >= number_input:
                mmW_data_accumulated.pop(0)
            mmW_data_accumulated.append(i)

        if len(mmW_data_accumulated) == number_input:
            predictions = model.predict([np.array(mmW_data_accumulated).reshape()])
            print('Prediction: ', class_names[np.argmax(predictions[0])])

    except KeyboardInterrupt:
        print("\nExiting.")
        thread1.join()
        break