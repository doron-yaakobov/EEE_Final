import os
import sys

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EEE_Final.settings")
# Add the path to your Django project's root directory
django_project_path = r"/"  # Replace with the actual path
sys.path.append(django_project_path)
# Configure Django settings
import django

django.setup()

import numpy as np
from scipy.signal import find_peaks
from patient_view.models import VitalSign, Patient
import serial
import serial.tools.list_ports as list_ports
from collections import deque

SAMPLING_RATE = 100  # Hz
PEAK_DISTANCE = 0.7  # Seconds
MAX_SATURATION = 100  # %
TIMEOUT = 1
COM_PORT = "COM7"
FREQUENCY = 100  # Hz
BAUD_RATE = 115200
MAX_DATA_POINTS = 15 * FREQUENCY  # sec * Hz
data = dict()

# region Test
TEST_DATA = r"C:\Users\dorony\PycharmProjects\EEE_Final\data.txt"


def import_django_for_testing():
    import os
    import sys

    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EEE_Final.settings")
    # Add the path to your Django project's root directory
    django_project_path = r"/"  # Replace with the actual path
    sys.path.append(django_project_path)
    # Configure Django settings
    import django
    django.setup()


def analyze_test_data(file: str = TEST_DATA):
    global data
    with open(file, "r") as file:
        for line in file:
            line = line.strip()

            if line:
                # print(line)
                is_valid_line, user_id, ir_value, red_value = extract_ppg_line(line)
                if is_valid_line:
                    data = update_ppg_data(user_id=user_id, ir_value=ir_value, red_value=red_value,
                                           pre_collected_ppg_data=data, max_data_points=MAX_DATA_POINTS)
                    ir_signal, red_signal = np.array(data[user_id]['ir_fifo']), np.array(data[user_id]['red_fifo'])

                    pulse_rate_bpm = calculate_pulse_rate(red_signal=red_signal, infrared_signal=ir_signal,
                                                          sampling_rate_hz=SAMPLING_RATE,
                                                          peak_distance_seconds=PEAK_DISTANCE)
                    oxygen_saturation_percent = calculate_spo2(red_signal=red_signal, infrared_signal=ir_signal)

                    if pulse_rate_bpm != 0 and len(red_signal) % 50 == 0:
                        save_vital_signs(user_id, oxygen_saturation_percent, pulse_rate_bpm)


def get_available_com_ports():
    available_ports = list_ports.comports()
    return [port.device for port in available_ports]


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


# endregion

def calculate_pulse_rate(red_signal: np.ndarray, infrared_signal: np.ndarray, sampling_rate_hz: int = SAMPLING_RATE,
                         peak_distance_seconds: float = PEAK_DISTANCE) -> int:
    """
    Calculate pulse rate from red and infrared PPG signals.

    Args:
        red_signal (numpy array): PPG signal from the red wavelength.
        infrared_signal (numpy array): PPG signal from the infrared wavelength.
        sampling_rate_hz (int): Sampling rate of the PPG signals in Hz.
        peak_distance_seconds (float): Define the time window for peak detection (adjust as needed)

    Returns:
        int: Estimated pulse rate in beats per minute (BPM).
    """

    # Find peaks in the red and infrared signals
    red_peaks, _ = find_peaks(red_signal, distance=int(sampling_rate_hz * peak_distance_seconds))
    infrared_peaks, _ = find_peaks(infrared_signal, distance=int(sampling_rate_hz * peak_distance_seconds))

    # Ensure there are detected peaks before proceeding
    if len(red_peaks) == 0 or len(infrared_peaks) == 0 or len(red_signal) <= 300 or len(infrared_signal) <= 300:
        return 0

    # Calculate time intervals between successive peaks
    red_intervals_seconds = np.diff(red_peaks) / sampling_rate_hz
    infrared_intervals_seconds = np.diff(infrared_peaks) / sampling_rate_hz
    # Choose which signal to use based on the number of detected peaks
    time_intervals_seconds = red_intervals_seconds if len(red_intervals_seconds) > len(infrared_intervals_seconds) \
        else infrared_intervals_seconds
    # Calculate pulse rate (beats per minute)
    pulse_rate_bpm = 60 / np.mean(time_intervals_seconds)
    return int(pulse_rate_bpm)


def calculate_spo2(red_signal: np.ndarray, infrared_signal: np.ndarray) -> int or None:
    """
    Calculate oxygen saturation (SpO2) from red and infrared PPG signals.

    Parameters:
        red_signal (list or numpy array): List of red PPG signal values.
        infrared_signal (list or numpy array): List of infrared PPG signal values.

    Returns:
        oxygen_saturation (int): Calculated oxygen saturation in percentage.
    """
    # Convert string arrays to numerical arrays
    red_signal = red_signal.astype(float)
    infrared_signal = infrared_signal.astype(float)

    # Check if the lengths of the red and infrared signals match
    if len(red_signal) != len(infrared_signal):
        return None

    # Calculate the AC components
    ac_red = np.max(red_signal) - np.min(red_signal)
    ac_ir = np.max(infrared_signal) - np.min(infrared_signal)
    # Calculate the ratio R
    r_ratio = ac_red / ac_ir
    # Calculate SpO2 using the calibration curve
    oxygen_saturation = min(MAX_SATURATION, 110 - (12 * r_ratio))
    return int(oxygen_saturation)


def save_vital_signs(patient_id: int, spo2: int, pulse_rate_bpm: int) -> None:
    patient = Patient.objects.get(patient_id=patient_id)
    vital_sign = VitalSign(patient=patient, spo2=spo2, heart_rate=pulse_rate_bpm)
    vital_sign.save()


def analyze_com_data(com_port=COM_PORT, baud_rate=BAUD_RATE, timeout=1):
    global data
    try:
        ser = serial.Serial(COM_PORT, baudrate=BAUD_RATE, timeout=1)
        while True:
            line = ser.readline().decode('utf-8').strip()

            if line:
                # print(line)
                is_valid_line, user_id, ir_value, red_value = extract_ppg_line(line)
                if is_valid_line:
                    data = update_ppg_data(user_id=user_id, ir_value=ir_value, red_value=red_value,
                                           pre_collected_ppg_data=data, max_data_points=MAX_DATA_POINTS)
                    ir_signal, red_signal = np.array(data[user_id]['ir_fifo']), np.array(data[user_id]['red_fifo'])

                    pulse_rate_bpm = calculate_pulse_rate(red_signal=red_signal, infrared_signal=ir_signal,
                                                          sampling_rate_hz=SAMPLING_RATE,
                                                          peak_distance_seconds=PEAK_DISTANCE)
                    oxygen_saturation_percent = calculate_spo2(red_signal=red_signal, infrared_signal=ir_signal)

                    if pulse_rate_bpm != 0 and len(red_signal) % 50 == 0:
                        save_vital_signs(user_id, oxygen_saturation_percent, pulse_rate_bpm)

    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Saving data has been interrupted.")

    finally:
        if ser.is_open:
            ser.close()


def extract_ppg_line(line: str) -> (bool, int, int, int):
    """
    Extract PPG data from a given line.

    Parameters:
        line (str): A single line of text containing PPG data.

    Returns:
        tuple: A tuple containing the extracted data.
               - User ID.
               - IR value.
               - Red value.
    """
    line = line.strip().split()
    is_valid_line = (len(line) == 3) and all(measure.isdigit() for measure in line)
    user_id, ir_value, red_value = line if is_valid_line else [None, None, None]
    return is_valid_line, user_id, ir_value, red_value


def update_ppg_data(user_id: int, ir_value: int, red_value: int,
                    pre_collected_ppg_data: dict, max_data_points: int = MAX_DATA_POINTS) -> dict:
    """
    Update PPG data for a specific user with new measurements.

    Parameters:
        user_id (int): The ID of the user.
        ir_value (int): The IR value measurement.
        red_value (int): The red value measurement.
        pre_collected_ppg_data (dict): A dictionary containing pre-collected user-specific PPG data.
                        The format is: {user_id: {'ir_fifo': deque, 'red_fifo': deque}}

    Returns:
        dict: An updated dictionary containing user-specific PPG data.
              The format is: {user_id: {'ir_fifo': deque, 'red_fifo': deque}}
    """

    is_new_user_id = user_id not in pre_collected_ppg_data
    if is_new_user_id:
        pre_collected_ppg_data[user_id] = {'ir_fifo': deque(maxlen=max_data_points),
                                           'red_fifo': deque(maxlen=max_data_points)}

    pre_collected_ppg_data[user_id]['ir_fifo'].append(ir_value)
    pre_collected_ppg_data[user_id]['red_fifo'].append(red_value)

    return pre_collected_ppg_data


if __name__ == '__main__':
    analyze_test_data()
