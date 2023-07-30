import re

# region init
patient_data = {}
file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE_v2.txt'


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


def read_ppg_data(file_path: str, ppg_data: dict) -> dict:
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


def detect_peaks(signal: list, threshold: float = 0.5) -> list:
    """
    Basic peak detection algorithm to find peaks in a signal.

    Parameters:
        signal (list): A list containing the PPG signal data.
        threshold (float): The threshold value used to identify peaks. The default value is 0.5.

    Returns:
        list: A list containing the indices of detected peaks in the signal.
    """
    peaks = []
    max_idx = len(signal) - 1

    for i in range(1, max_idx):
        if signal[i] > threshold and signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
            peaks.append(i)
    return peaks


def main():
    global patient_data
    global file_path

    patient_data = read_ppg_data(file_path, patient_data)

    # region Peak Detection for each user -> patient_data.patient_id.(ir_peaks_idx & red_peaks_idx)
    for pat_id, pat_data in patient_data.items():
        # region init
        ir_fifo = pat_data['ir_fifo']
        red_fifo = pat_data['red_fifo']
        # endregion

        ir_peaks_idx = detect_peaks(ir_fifo)
        red_peaks_idx = detect_peaks(red_fifo)

        pat_data['ir_peaks_idx'] = ir_peaks_idx if ("ir_peaks_idx" not in pat_data) else (
                pat_data['ir_peaks_idx'] + ir_peaks_idx)
        pat_data['red_peaks_idx'] = red_peaks_idx if ("red_peaks_idx" not in pat_data) else (
                pat_data['red_peaks_idx'] + red_peaks_idx)
    # endregion

    # time_in_msec = pat_data['time_in_msec']

    # region Cleanup Analyzed PPG measures
    for pat_id in patient_data:
        patient_data[pat_id]["ir_fifo"] = []
        patient_data[pat_id]["red_fifo"] = []
    # endregion


if __name__ == "__main__":
    main()
