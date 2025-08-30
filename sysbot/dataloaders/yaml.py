import yaml


def load(file):
    """
    Load variables from a YAML file.

    :param file_path: Path to the YAML file.
    :type file_path: str
    :return: Parsed content of the YAML file.
    :rtype: dict or list
    :raises FileNotFoundError: If the specified YAML file does not exist.
    :raises RuntimeError: If there is an error parsing the YAML file.
    :raises RuntimeError: If an unexpected error occurs during processing.
    """
    file_path = file
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file not found: {file_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML file: {file_path} - {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error occurred while loading YAML: {e}")
