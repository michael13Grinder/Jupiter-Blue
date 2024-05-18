import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import struct  # for unpacking binary data
import time

# Function to initialize serial connections with different baud rates
def init_serial_connections(data_port, config_port, data_baudrate=921600, config_baudrate=115200, timeout=1):
    try:
        data_serial = serial.Serial(data_port, baudrate=data_baudrate, timeout=timeout)
        config_serial = serial.Serial(config_port, baudrate=config_baudrate, timeout=timeout)
        print(f"Connected to {data_port} at {data_baudrate} baud and {config_port} at {config_baudrate} baud.")
        return data_serial, config_serial
    except serial.SerialException as e:
        print(f"Error: {e}")
        return None, None

# Function to read radar data from the data serial port
def read_radar_data(data_serial, packet_size):
    try:
        buffer = bytearray()
        while len(buffer) < packet_size:
            packet = data_serial.read(packet_size - len(buffer))
            buffer.extend(packet)
        
        # Unpack the binary data into an array of floats
        num_floats = packet_size // 4  # 4 bytes per float
        data = struct.unpack(f'{num_floats}f', buffer)
        data = np.array(data).reshape(-1, 2)
        
        return data
    except Exception as e:
        print(f"Error reading data: {e}")
        return np.empty((0, 2))

# Function to process the radar data
def process_radar_data(data):
    # Extract range and Doppler values
    if data.size > 0:
        ranges = data[:, 0]
        dopplers = data[:, 1]
    else:
        ranges = np.array([])
        dopplers = np.array([])
    return ranges, dopplers

# Initialize serial connections (adjust ports as needed)
data_port = 'COM8'     # Replace with the actual data port
config_port = 'COM3'   # Replace with the actual configuration port
data_baudrate = 921600  # Baud rate for data port
config_baudrate = 115200 # Baud rate for configuration port

# Known packet size (number of bytes per packet from the radar)
# Adjust this according to the radar's output packet size.
# For example, if each packet contains 50 pairs of (range, Doppler) values:
num_pairs = 50
packet_size = num_pairs * 2 * 4  # 2 floats (range and Doppler) * 4 bytes per float

data_serial, config_serial = init_serial_connections(data_port, config_port, data_baudrate, config_baudrate)

if data_serial is None or config_serial is None:
    print("Failed to initialize serial connections. Exiting.")
else:
    # Set up the plot
    fig, ax = plt.subplots()
    sc = ax.scatter([], [], c='green')
    ax.set_xlim(0, 6)
    ax.set_ylim(-1, 1)
    ax.set_title('Doppler-Range Plot')
    ax.set_xlabel('Range (meters)')
    ax.set_ylabel('Doppler (m/s)')
    ax.grid(True)

    def update(frame):
        data = read_radar_data(data_serial, packet_size)
        ranges, dopplers = process_radar_data(data)

        # Debug: Print the ranges and dopplers
        print(f"Ranges: {ranges}")
        print(ranges.shape)
        print(f"Dopplers: {dopplers}")
        print(dopplers.shape)

        if ranges.size > 0 and dopplers.size > 0:
            sc.set_offsets(np.c_[ranges, dopplers])
        return sc,

    ani = FuncAnimation(fig, update, interval=100)
    plt.show()

    try:
        while True:
            # Keeping the main thread alive
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopped by User")

    finally:
        data_serial.close()
        config_serial.close()
