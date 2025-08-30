import csv


def load(file):
    """
    Load variables from a CSV file.

    :param file: Path to the CSV file.
    :type file: str
    :return: A list of dictionaries representing rows in the CSV file.
    :rtype: list[dict]
    :raises FileNotFoundError: If the specified CSV file does not exist.
    :raises RuntimeError: If there is an error reading the CSV file.
    :raises RuntimeError: If an unexpected error occurs during processing.
    """
    file_path = file
    try:
        result = []
        with open(file_path, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                result.append(row)
        return result
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except csv.Error as e:
        raise RuntimeError(f"Error reading CSV file: {file_path} - {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error occurred while loading CSV: {e}")
