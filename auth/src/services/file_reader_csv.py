#file_reader_csv.py
import os
import csv
from pathlib import Path

def find_csv_file_in_db_folder(filename):
    """
    Find a CSV file in the 'db' folder of the FastAPI application.

    Args:
        filename (str): The name of the CSV file to locate.

    Returns:
        str or None: The full path to the CSV file if found, or None if not found.
    """
    # Get the path to the 'db' folder within the FastAPI application
    db_folder = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db'))
    print(db_folder)
    # Search for the CSV file in the 'db' folder
    csv_path = db_folder / filename
    print(csv_path)
    if csv_path.is_file():
        return str(csv_path)
    else:
        return None


def read_userdata_csv(filename) -> list[dict()]:
    """
    Open and read user data from a CSV file.

    Args:
        file (file): A file object representing the CSV file containing user data.

    Returns:
        list: A list containing dictionaries, where each dictionary represents a user with key-value pairs.

    Note:
        The CSV file is expected to have a header row containing field names.

    Example:
        Assuming the CSV file has the following structure:
        username,password,role
        alice,password123,user
        bob,secret456,admin

        The resulting list may look like:
        [
            {"username": "alice", "password": "password123", "role": "user"},
            {"username": "bob", "password": "secret456", "role": "admin"}
        ]
    """
    
    #filename = find_csv_file_in_db_folder(filename)
    
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        users = list(reader)
    
    return users