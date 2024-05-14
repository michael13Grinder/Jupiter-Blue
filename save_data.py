import numpy as np
import threading
import time
import sys
sys.path.insert(1, 'AWR1843-Read-Data-Python-MMWAVE-SDK-3--master')
import readData_AWR1843

def format_data(input_data):
    num_objects = input_data['numObj']
    formatted_data = []
    
    for i in range(num_objects):
        x_i = input_data['x'][i]
        y_i = input_data['y'][i]
        z_i = input_data['z'][i]
        v_i = input_data['velocity'][i]
        
        formatted_data.append([x_i, y_i, z_i, v_i])
    
    return formatted_data

def flatten_list_data(input_data):
    num_objects = input_data['numObj']
    flattened_data = []
    
    for i in range(num_objects):
        flattened_data.append(input_data['x'][i])
        flattened_data.append(input_data['y'][i])
        flattened_data.append(input_data['z'][i])
        flattened_data.append(input_data['velocity'][i])
    
    return flattened_data

def flatten_data(input_data):
    num_objects = input_data['numObj']
    flattened_data = []
    
    for i in range(num_objects):
        flattened_data.append(input_data['x'][i])
    for i in range(num_objects):
        flattened_data.append(input_data['y'][i])
    for i in range(num_objects):
        flattened_data.append(input_data['z'][i])
    for i in range(num_objects):
        flattened_data.append(input_data['velocity'][i])
    
    return flattened_data

def get_velocity(input_data):
    num_objects = input_data['numObj']
    velocity_data = []
    
    for i in range(num_objects):
        velocity_data.append(input_data['velocity'][i])
    
    while len(velocity_data) < 12:
        velocity_data.append(0)
    
    velocity_data = velocity_data[:11]

    return velocity_data


# Open files for appending data
X_train_file = open("X_train.txt", "a")
y_train_gesture_file = open("y_train_gesture.txt", "a")

thread1 = threading.Thread(target=readData_AWR1843.main)
thread1.start()

time.sleep(2)

while True:
    try:
        # Simulate user input for gesture label
        gesture_label = input("Enter the gesture label (e.g., left): ")

        # Accumulate mmW data for 15 samples
        mmW_data_accumulated = []
        for _ in range(15):
            mmW_data = None
            while (mmW_data is None):
                mmW_data = readData_AWR1843.get_data()

            mmW_data = get_velocity(mmW_data)

            # print(len(mmW_data))
        
            for value in mmW_data:
                mmW_data_accumulated.append(value)
            
            time.sleep(0.5 / 15)
        
        print(len(mmW_data_accumulated))
        # print(len(mmW_data_accumulated) / (6*4))

        if not mmW_data_accumulated:
            continue

        # Save mmW data to X_train file
        X_train_file.write(' '.join(map(str, mmW_data_accumulated)) + '\n')

        gesture_encoding = "0"
        if (gesture_label == "none"):
            gesture_encoding = "0"
        elif (gesture_label == "left"):
            gesture_encoding = "1"
        elif (gesture_label == "right"):
            gesture_encoding = "2"
        elif (gesture_label == "up"):
            gesture_encoding = "3"
        elif (gesture_label == "down"):
            gesture_encoding = "4"

        # Append gesture label to y_train_gesture file
        y_train_gesture_file.write(gesture_encoding + '\n')

        print("Data saved successfully.")

    except KeyboardInterrupt:
        print("\nExiting.")
        # Close files
        X_train_file.close()
        y_train_gesture_file.close()

        thread1.join()

        break


