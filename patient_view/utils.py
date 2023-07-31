import numpy as np
from scipy.signal import find_peaks
from .models import VitalSign, Patient

SAMPLING_RATE = 100  # Hz
PEAK_DISTANCE = 0.7  # Seconds
MAX_SATURATION = 100  # %


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
    # Check if the lengths of the red and infrared signals match
    if len(red_signal) != len(infrared_signal):
        return None
    # Simple AC components:
    ac_red = max(red_signal) - min(red_signal)
    ac_ir = max(infrared_signal) - min(infrared_signal)
    # Calculate the ratio R
    r_ratio = ac_red / ac_ir
    # Calculate SpO2 using the calibration curve
    oxygen_saturation = min(MAX_SATURATION, 110 - (12 * r_ratio))
    return int(oxygen_saturation)


def save_vital_signs(patient_id: int, spo2: int, pulse_rate_bpm: int) -> None:
    patient = Patient.objects.get(patient_id=patient_id)
    vital_sign = VitalSign(patient=patient, spo2=spo2, heart_rate=pulse_rate_bpm)
    vital_sign.save()
