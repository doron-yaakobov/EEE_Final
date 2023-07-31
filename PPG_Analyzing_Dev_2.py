import os
import sys

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EEE_Final.settings")
# Add the path to your Django project's root directory
django_project_path = r"C:\Users\dorony\PycharmProjects\EEE_Final"  # Replace with the actual path
sys.path.append(django_project_path)
# Configure Django settings
import django

django.setup()

import re
import numpy as np
import patient_view.utils as utils

# region init
# data = {311252977: {'ir_fifo': [], 'pulse_rate_bpm': [80], 'red_fifo': [], 'res_time_in_msec': [170000], 'spo2_percent': [99], 'time_in_msec': []}}
data = {}
file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE_v2.txt'


# endregion
# region Load data utils:
def time_to_milliseconds(time_str: str) -> int:
    """
    Convert time in the format 'HH:MM:SS.mSec' to an integer representing total milliseconds.

    Parameters:
        time_str (str): A time string in the format 'HH:MM:SS.mSec'.

    Returns:
        int: Total milliseconds.

    Example:
        time_str = '00:01:23.456'
        milliseconds = time_to_milliseconds(time_str)
        # Output: 83456
    """
    # region split to components
    hours, minutes, seconds_msec = time_str.split(':')
    seconds, milliseconds = seconds_msec.split('.')
    # endregion 

    # Calculate the total milliseconds
    total_in_milliseconds = (int(hours) * 3600 + int(minutes) * 60 + int(seconds)) * 1000 + int(milliseconds)

    return total_in_milliseconds


def extract_ppg_line(line: str) -> (int, int, int, int):
    """
    Extract PPG data from a given line.

    Parameters:
        line (str): A single line of text containing PPG data.

    Returns:
        tuple: A tuple containing the extracted data.
               - The first element is the time, presented as int [mSec].
               - The second element is the user ID.
               - The third element is the IR value.
               - The fourth element is the red value.
    """
    pattern = r'\[(\d+:\d+:\d+\.\d+),\d+\].*?(\d+)\s+(\d+)\s+(\d+)'
    match = re.search(pattern, line)
    if match:
        time = time_to_milliseconds(match.group(1))
        user_id = int(match.group(2))
        ir_value = int(match.group(3))
        red_value = int(match.group(4))

        return time, user_id, ir_value, red_value
    else:
        return None, None, None, None


def parse_and_load_ppg_data(file_path: str, ppg_data: dict) -> dict:
    """
    Read PPG data from the given file and return a dictionary containing user-specific data.

    Parameters:
        file_path (str): The path to the file containing PPG data.
        ppg_data (dict): A dictionary containing pre-collected user-specific PPG data.
                        The format is: {user_id: {'ir_fifo': [<data>], 'red_fifo': [<data>]}}

    Returns:
        dict: A dictionary containing aggregated user-specific PPG data.
              The format is: {user_id: {'ir_fifo': [<data>], 'red_fifo': [<data>]}}

    """

    with open(file_path, 'r') as file:
        for line in file:
            time, user_id, ir_value, red_value = extract_ppg_line(line.strip())
            is_dummy_line = None in (time, user_id, ir_value, red_value)
            if is_dummy_line:
                continue

            # region initiate new user_id
            is_new_user_id = user_id not in ppg_data
            if is_new_user_id:
                # ppg_data[user_id] = {'time_in_msec': [], 'ir_fifo': [], 'red_fifo': []}
                ppg_data[user_id] = {'ir_fifo': [], 'red_fifo': []}
            # endregion
            # ppg_data[user_id]['time_in_msec'].append(time)
            ppg_data[user_id]['ir_fifo'].append(ir_value)
            ppg_data[user_id]['red_fifo'].append(red_value)
    return ppg_data


# endregion


def main():
    while True:

        global data
        data = parse_and_load_ppg_data(file_path, data)  # TODO: update to read from COM

        for patient_id, ppg_data in data.items():
            red_signal = np.array(ppg_data['red_fifo'])
            ir_signal = np.array(ppg_data['ir_fifo'])

            pulse_rate_bpm = utils.calculate_pulse_rate(red_signal=red_signal, infrared_signal=ir_signal,
                                                        sampling_rate_hz=utils.SAMPLING_RATE,
                                                        peak_distance_seconds=utils.PEAK_DISTANCE)
            oxygen_saturation_percent = utils.calculate_spo2(red_signal=red_signal, infrared_signal=ir_signal)
            utils.save_vital_signs(patient_id, oxygen_saturation_percent, pulse_rate_bpm)

        # region Cleanup Analyzed PPG measures, making place for next measures.
        for _, ppg_data in data.items():
            ppg_data["ir_fifo"] = []
            ppg_data["red_fifo"] = []
        # endregion
        pass


if __name__ == "__main__":
    main()
