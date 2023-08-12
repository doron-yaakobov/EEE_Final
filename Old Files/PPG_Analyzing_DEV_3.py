import asyncio
import serial
import numpy as np

# Assuming 'utils' contains your utility functions for calculating pulse rate and oxygen saturation
# and saving vital signs.

# Global variable to store the PPG data
data = {}


async def read_com_data(com_port, baud_rate, ppg_data):
    try:
        # Open the COM port
        ser = serial.Serial(com_port, baud_rate)
        print(f"Serial port {com_port} opened.")

        while True:
            # Read one line from the COM port
            line = ser.readline().decode('utf-8').strip()

            # Extract PPG data from the line
            time, user_id, ir_value, red_value = extract_ppg_line(line)
            is_dummy_line = None in (time, user_id, ir_value, red_value)
            if is_dummy_line:
                continue

            # region initiate new user_id
            is_new_user_id = user_id not in ppg_data
            if is_new_user_id:
                ppg_data[user_id] = {'ir_fifo': [], 'red_fifo': []}
            # endregion

            # Add PPG data to the dictionary
            ppg_data[user_id]['ir_fifo'].append(ir_value)
            ppg_data[user_id]['red_fifo'].append(red_value)

            # Control the reading frequency to 100 Hz (10 milliseconds delay)
            await asyncio.sleep(0.01)

    except asyncio.CancelledError:
        # Close the COM port on cancellation
        ser.close()
        print(f"Serial port {com_port} closed.")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")


async def main():
    global data

    # Initialize the data dictionary
    data = {}

    # Start the data acquisition task in the background
    com_port = 'COM3'

