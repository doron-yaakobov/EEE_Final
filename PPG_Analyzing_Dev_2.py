import gc
import re
import numpy as np
from scipy.signal import find_peaks

# region init
# data = {311252977: {'ir_fifo': [], 'pulse_rate_bpm': [80], 'red_fifo': [], 'res_time_in_msec': [170000], 'spo2_percent': [99], 'time_in_msec': []}}
data = {}
file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE_v2.txt'
SAMPLING_RATE = 100  # Hz


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
                ppg_data[user_id] = {'time_in_msec': [], 'ir_fifo': [], 'red_fifo': []}
            # endregion
            ppg_data[user_id]['time_in_msec'].append(time)
            ppg_data[user_id]['ir_fifo'].append(ir_value)
            ppg_data[user_id]['red_fifo'].append(red_value)
    return ppg_data


# endregion

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


def calculate_spo2(red_signal: np.ndarray, infrared_signal: np.ndarray) -> float or None:
    """
    Calculate oxygen saturation (SpO2) from red and infrared PPG signals.

    Parameters:
        red_signal (list or numpy array): List of red PPG signal values.
        infrared_signal (list or numpy array): List of infrared PPG signal values.

    Returns:
        oxygen_saturation (float): Calculated oxygen saturation in percentage.
    """
    # Check if the lengths of the red and infrared signals match
    if len(red_signal) != len(infrared_signal):
        return None

    # Simple AC components:
    ac_red = max(red_signal) - min(red_signal)
    ac_ir = max(infrared_signal) - min(infrared_signal)
    # Calculate the ratio R
    r_ratio = ac_red / ac_ir
    # Calculate SpO2 using the calibration curve
    oxygen_saturation = min(100, 110 - (12 * r_ratio))

    return oxygen_saturation


# region Save utils:
def save_pulse_rate(patient_data: dict, pulse_rate_bpm: float) -> dict:
    if "pulse_rate_bpm" in patient_data:
        patient_data["pulse_rate_bpm"].append(pulse_rate_bpm)
    else:
        patient_data["pulse_rate_bpm"] = [pulse_rate_bpm]
    return patient_data


def save_res_time(patient_data: dict, res_time_in_msec: int) -> dict:
    if "res_time_in_msec" in patient_data:
        if patient_data["res_time_in_msec"][-1] >= res_time_in_msec:
            patient_data["res_time_in_msec"].append(res_time_in_msec + patient_data["res_time_in_msec"][-1])
        else:
            patient_data["res_time_in_msec"].append(res_time_in_msec)
    else:
        patient_data["res_time_in_msec"] = [res_time_in_msec]
    return patient_data


def save_spo2(patient_data: dict, spo2: float) -> dict:
    if "spo2_percent" in patient_data:
        patient_data["spo2_percent"].append(spo2)
    else:
        patient_data["spo2_percent"] = [spo2]
    return patient_data


# endregion

def main():
    global data
    global file_path

    while True:
        data = parse_and_load_ppg_data(file_path, data)

        for patient_id, patient_data in data.items():
            # region INIT
            red_signal = np.array(patient_data['red_fifo'])
            ir_signal = np.array(patient_data['ir_fifo'])
            last_measure_time = patient_data["time_in_msec"][-1]
            # endregion
            pulse_rate_bpm = calculate_pulse_rate(red_signal=red_signal, infrared_signal=ir_signal)
            oxygen_saturation_percent = calculate_spo2(red_signal=red_signal, infrared_signal=ir_signal)
            # region save results
            patient_data = save_pulse_rate(patient_data, pulse_rate_bpm)
            patient_data = save_res_time(patient_data, last_measure_time)
            patient_data = save_spo2(patient_data, oxygen_saturation_percent)
            # endregion

        # region Cleanup Analyzed PPG measures, making place for next measures.
        for _, patient_data in data.items():
            patient_data["ir_fifo"] = []
            patient_data["red_fifo"] = []
            patient_data["time_in_msec"] = []
            gc.collect()
        # endregion
        pass


if __name__ == "__main__":
    main()