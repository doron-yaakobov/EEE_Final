import serial
import time
import serial.tools.list_ports

COM_PORT = "COM3"
FREQUENCY = 100  # Hz
BAUD_RATE = 9600


def get_available_com_ports():
    available_ports = serial.tools.list_ports.comports()
    return [port.device for port in available_ports]


def send_lines_to_com_port(ser, file_path, com_port=COM_PORT, baud_rate=9600, frequency=FREQUENCY):
    try:
        # Open the COM port
        # ser = serial.Serial(com_port, baud_rate)
        # print(f"Serial port {com_port} opened.")

        # Read lines from the file
        with open(file_path, 'r') as file:
            lines = file.readlines()

        # Calculate the delay between sending lines to achieve the desired frequency
        delay = 1 / frequency

        # Send each line one by one
        for line in lines:
            # Remove newline character
            line = line.strip()

            # Send the line to the COM port
            ser.write(line.encode('utf-8'))

            # Wait for the next line to be sent to achieve the desired frequency
            time.sleep(delay)

        # Close the COM port
        # ser.close()
        # print("Serial port closed.")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")


available_com_ports = get_available_com_ports()
print("Available COM ports:", available_com_ports)

file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE_v2.txt'
ser = serial.Serial(COM_PORT, BAUD_RATE)
print(f"Serial port {COM_PORT} opened.")

while 1:
    send_lines_to_com_port(ser, file_path, com_port=COM_PORT, baud_rate=BAUD_RATE, frequency=FREQUENCY)

ser.close()
print("Serial port closed.")
