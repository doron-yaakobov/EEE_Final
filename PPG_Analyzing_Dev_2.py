import re
import numpy as np
from scipy.signal import find_peaks

# region init
data = {311252977: {'ir_fifo': [], 'pulse_rate_bpm': [75.70977917981071], 'red_fifo': [], 'res_time_in_msec': [164387],
                    'time_in_msec': []}}
# data = {}
file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE_v2.txt'
SAMPLING_RATE = 100  # Hz


# endregion


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
                ppg_data[user_id] = {'time_in_msec': [], 'ir_fifo': [], 'red_fifo': []}
            # endregion
            ppg_data[user_id]['time_in_msec'].append(time)
            ppg_data[user_id]['ir_fifo'].append(ir_value)
            ppg_data[user_id]['red_fifo'].append(red_value)
    return ppg_data


def calculate_pulse_rate(red_signal: np.ndarray, infrared_signal: np.ndarray, sampling_rate_hz: int = SAMPLING_RATE,
                         peak_distance_seconds: float = 0.7) -> float:
    """
    Calculate pulse rate from red and infrared PPG signals.

    Args:
        red_signal (numpy array): PPG signal from the red wavelength.
        infrared_signal (numpy array): PPG signal from the infrared wavelength.
        sampling_rate_hz (int): Sampling rate of the PPG signals in Hz.
        peak_distance_seconds (float): Define the time window for peak detection (adjust as needed)

    Returns:
        float: Estimated pulse rate in beats per minute (BPM).
    """

    # Find peaks in the red and infrared signals
    red_peaks, _ = find_peaks(red_signal, distance=int(sampling_rate_hz * peak_distance_seconds))
    infrared_peaks, _ = find_peaks(infrared_signal, distance=int(sampling_rate_hz * peak_distance_seconds))

    # Calculate time intervals between successive peaks
    red_intervals_seconds = np.diff(red_peaks) / sampling_rate_hz
    infrared_intervals_seconds = np.diff(infrared_peaks) / sampling_rate_hz

    # Choose which signal to use based on the number of detected peaks
    time_intervals_seconds = red_intervals_seconds if len(red_intervals_seconds) > len(infrared_intervals_seconds) \
        else infrared_intervals_seconds

    # Calculate pulse rate (beats per minute)
    pulse_rate_bpm = 60 / np.mean(time_intervals_seconds)

    return pulse_rate_bpm


def main():
    global data
    global file_path

    data = parse_and_load_ppg_data(file_path, data)

    # region Calculate Pulse Rate
    for patient_id, patient_data in data.items():
        # region INIT
        red_signal = np.array(patient_data['red_fifo'])
        ir_signal = np.array(patient_data['ir_fifo'])
        last_measure_time = patient_data["time_in_msec"][-1]
        # endregion
        pulse_rate_bpm = calculate_pulse_rate(red_signal=red_signal, infrared_signal=ir_signal)
        # region save results
        if "pulse_rate_bpm" in patient_data:
            patient_data["pulse_rate_bpm"].append(pulse_rate_bpm)
        else:
            patient_data["pulse_rate_bpm"] = [pulse_rate_bpm]

        if "res_time_in_msec" in patient_data:
            if last_measure_time <= patient_data["res_time_in_msec"][-1]:
                last_measure_time = patient_data["res_time_in_msec"][-1] + last_measure_time
            patient_data["res_time_in_msec"].append(last_measure_time)
        else:
            patient_data["res_time_in_msec"] = [last_measure_time]

        # endregion
    # endregion

    # region Cleanup Analyzed PPG measures, making place for next measures.
    for _, patient_data in data.items():
        patient_data["ir_fifo"] = []
        patient_data["red_fifo"] = []
        patient_data["time_in_msec"] = []
    # endregion


if __name__ == "__main__":
    main()
