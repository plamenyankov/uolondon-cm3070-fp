import pandas as pd
import os

class DataLoader:

    @staticmethod
    def load_data(file_path):
        """
        Loads the data from the specified file path.

        :param file_path: Path to the data file.
        :return: A pandas DataFrame containing the loaded data.
        """
        if DataLoader._is_valid_file(file_path):
            return pd.read_csv(file_path)
        else:
            print("Invalid file path or unsupported file type.")
            return None

    @staticmethod
    def _is_valid_file(file_path):
        """
        Checks if the file exists and is a supported type.

        :param file_path: Path to the data file.
        :return: True if the file is valid, False otherwise.
        """
        return file_path.endswith('.csv') and os.path.exists(file_path)
