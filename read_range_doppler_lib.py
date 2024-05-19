import numpy as np
import serial
import struct  # for unpacking binary data

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