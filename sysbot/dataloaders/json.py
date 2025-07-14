import json

def load(file):
    """
    Load variables from a JSON file.

    :param file: Path to the JSON file.
    :type file: str
    :return: Parsed content of the JSON file.
    :rtype: dict or list
    :raises FileNotFoundError: If the specified JSON file does not exist.
    :raises RuntimeError: If there is an error decoding the JSON file.
    :raises RuntimeError: If an unexpected error occurs during processing.
    """
    file_path = file
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error decoding JSON file: {file_path} - {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error occurred while loading JSON: {e}")
