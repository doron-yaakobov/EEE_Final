def read_ppg_data(file_path):
    """
    Read PPG data from the given file and return a dictionary containing user-specific data.

    Parameters:
        file_path (str): The path to the file containing PPG data.

    Returns:
        dict: A dictionary containing user-specific PPG data.
              The format is: {user_id: {'ir_fifo': [<data>], 'red_fifo': [<data>]}}
    """
    ppg_data = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            is_data = line[0].isdigit()

            if not is_data:
                continue

            user_id, ir_value, red_value = map(int, line.split())  # extract data
            is_new_user_id = user_id not in ppg_data

            if is_new_user_id:
                ppg_data[user_id] = {'ir_fifo': [], 'red_fifo': []}

            ppg_data[user_id]['ir_fifo'].append(ir_value)
            ppg_data[user_id]['red_fifo'].append(red_value)

    return ppg_data


def main():
    # File path
    file_path = r'C:\Users\dorony\PycharmProjects\EEE_Final\PPG_EXAMPLE.txt'

    # Step 1: Read PPG data from the file
    ppg_data = read_ppg_data(file_path)


if __name__ == "__main__":
    main()
