import csv
import json
import yaml

from sysbot.utils.engine import ComponentBase


class Data(ComponentBase):
    @staticmethod
    def csv(file: str) -> list[dict]:
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

    @staticmethod
    def json(file: str) -> dict:
        file_path = file
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading JSON: {e}")

    @staticmethod
    def yaml(file: str) -> dict:
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
