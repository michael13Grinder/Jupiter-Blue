import numpy as np
import threading
import signal
from queue import Queue
import time
import sys
sys.path.insert(1, 'AWR1843-Read-Data-Python-MMWAVE-SDK-3--master')
import readData_AWR1843

# Create a queue for communication
quit_queue = Queue()

# Signal handler function
def signal_handler(sig, frame):
    print("\nKeyboard Interrupt received. Signaling thread to quit.")
    quit_queue.put(True)

# Register the signal handler for SIGINT (Keyboard Interrupt)
signal.signal(signal.SIGINT, signal_handler)

# Open files for appending data
X_train_file = open("X_train.txt", "a")
y_train_gesture_file = open("y_train_gesture.txt", "a")

thread1 = threading.Thread(target=readData_AWR1843.main, args=(quit_queue,))
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
        
            for value in mmW_data:
                mmW_data_accumulated.append(value)

        if not mmW_data_accumulated:
            continue

        # Save mmW data to X_train file
        X_train_file.write(','.join(map(str, mmW_data_accumulated)) + '\n')

        # Append gesture label to y_train_gesture file
        y_train_gesture_file.write(gesture_label + '\n')

        print("Data saved successfully.")

    except KeyboardInterrupt:
        print("\nExiting.")
        # Close files
        X_train_file.close()
        y_train_gesture_file.close()

        time.sleep(1)

        thread1.join()


