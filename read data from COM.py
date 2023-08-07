import serial
import threading
from send_data_to_com import *

# try:
#     ser = serial.Serial(COM_PORT, BAUD_RATE)
#     print(f"Connected to {COM_PORT} at {BAUD_RATE} baud.")
# except serial.SerialException:
#     print("Failed to connect to the COM port. Check the port and baud rate settings.")
#     exit()
# while True:
#     line = ser.readline().decode().strip()
#     print(f"Received: {line}")
#
#     if line == 'exit':
#         break
# ser.close()
#
# # Initialize serial connection
# ser = serial.Serial(COM_PORT, BAUD_RATE)
#
#
# while True:
#     # Read line from serial port
#     data = ser.readline().decode().strip()
#     print(f"{data}")
#
# ser.close()




"""
sample: 
Received: [00:07:43.696,350] <inf> CENTRAL: notify_func: 311252977 81469 64070
Received: [00:07:43.746,337] <inf> CENTRAL: notify_func: 311252977 81496 64080
Received: [00:07:43.896,667] <inf> CENTRAL: notify_func: 311252977 81472 64063
Received: [00:07:43.897,186] <inf> CENTRAL: notify_func: 311252977 81466 64054
Received: [00:07:43.996,337] <inf> CENTRAL: notify_func: 311252977 81432 64014
Received: [00:07:44.096,343] <inf> CENTRAL: notify_func: 311252977 81400 63982
Received: [00:07:44.146,362] <inf> CENTRAL: notify_func: 311252977 81391 63968
Received: [00:07:44.246,337] <inf> CENTRAL: notify_func: 311252977 81388 63972
Received: [00:07:44.346,343] <inf> CENTRAL: notify_func: 311252977 81393 63976


<ID> <ir> <RED>
10 SEC at least per mesure * 100HZ = 1000 pulses at least. 
"""


import serial

def save_com_data_to_file(com_port, file_name):
    try:
        # Open the COM port
        ser = serial.Serial(COM_PORT, baudrate=BAUD_RATE, timeout=1)

        # Open the file in write mode
        with open(file_name, 'w') as file:
            while True:
                # Read data from the COM port
                line = ser.readline().decode('utf-8').strip()

                # Check if data is not empty
                if line:
                    # Write data to the file with the "Received:" prefix
                    file.write(line + '\n')
                    file.flush()  # Flush the buffer to ensure data is written immediately

    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Saving data has been interrupted.")
    finally:
        if ser.is_open:
            ser.close()

if __name__ == "__main__":
    com_port = 'COM7'
    file_name = 'data.txt'
    save_com_data_to_file(com_port, file_name)
