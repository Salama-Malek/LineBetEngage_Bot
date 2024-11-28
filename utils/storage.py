import json
import os

USER_DATA_FILE = 'user_data.json'

def save_user_data(user_id, data):
    """
    Saves user data to a JSON file.

    Args:
        user_id (int): The user's unique Telegram ID.
        data (dict): The data to save for the user.
    """
    try:
        # Load existing data
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                user_data = json.load(f)
        else:
            user_data = {}

        # Update the user's data
        user_data[str(user_id)] = data

        # Save back to the file
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=4)
    except Exception as e:
        print(f"Error saving user data: {e}")

def load_user_data(user_id):
    """
    Loads user data from a JSON file.

    Args:
        user_id (int): The user's unique Telegram ID.

    Returns:
        dict or None: The user's data if it exists, otherwise None.
    """
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                user_data = json.load(f)
            return user_data.get(str(user_id))
        else:
            return None
    except Exception as e:
        print(f"Error loading user data: {e}")
        return None

def get_all_user_data():
    """
    Retrieves all user data from the JSON file.

    Returns:
        dict: All user data stored in the file.
    """
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading all user data: {e}")
        return {}
