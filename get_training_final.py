import numpy as np
import time
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

X_train_file = open("X_train.txt", "a")
y_train_gesture_file = open("y_train_gesture.txt", "a")
gesture_list = ['idle', 'left', 'right', 'up', 'down']
count = 0

while True:
    try:
        gesture_label = input("Enter the gesture label (e.g., left): ")
        if gesture_label not in gesture_list:
            print('Gesture not included')
            continue

        # Accumulate mmW data for 15 samples
        accumulate_data = None
        for i in range(15):
            data = rangeDopplerLib.read_radar_data(data_serial, packet_size)
            ranges, dopplers = rangeDopplerLib.process_radar_data(data)
            if ranges.size == 50 and dopplers.size == 50:
                rangeDoppler = np.append(ranges, dopplers)
            else:
                rangeDoppler = None
            if isinstance(rangeDoppler, np.ndarray):
                if not isinstance(accumulate_data, np.ndarray):
                    accumulate_data = rangeDoppler.copy()
                    accumulate_data = np.expand_dims(accumulate_data, axis=0)
                else:
                    rangeDoppler = np.expand_dims(rangeDoppler, axis=0)
                    accumulate_data = np.append(accumulate_data, rangeDoppler, axis=0)
            else:
                i -= 1
                continue
            time.sleep(0.03)
        np.savetxt(X_train_file, accumulate_data, fmt='%1.4f')
        count += 1
        print(count)
        gesture_encoding = "0"
        if (gesture_label == "idle"):
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

    except KeyboardInterrupt:
        print("Stopped by User")
        data_serial.close()
        config_serial.close()
        break
