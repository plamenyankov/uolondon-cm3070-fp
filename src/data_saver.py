import pandas as pd
import os
import re

class DataSaver:

    def save_to_csv(self, dataframe, path):
        """
        Save a DataFrame to a CSV file.

        :param dataframe: The pandas DataFrame to save.
        :param path: The full path to the desired file (directory + filename).
        """
        if os.path.exists(path):
            action = input(f"File {path} already exists! Overwrite (O), Append (A), Cancel (C)? ").upper()
            if action == 'O':
                dataframe.to_csv(path, index=False)
                print(f"Data saved to: {path}")
            elif action == 'A':
                dataframe.to_csv(path, mode='a', header=False, index=False)
                print(f"Data appended to: {path}")
            elif action == 'C':
                print("Save operation cancelled.")
            else:
                print(f"Unknown action: {action}. Save operation cancelled.")
        else:
            dataframe.to_csv(path, index=False)
            print(f"Data saved to: {path}")
    @staticmethod
    def format_path(path):
        file_name = f"{path}".lower().replace(" ", "_")
        return file_name

