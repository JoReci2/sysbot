"""
Data Plugin Module

This module provides functionality for loading and managing data from various
file formats (CSV, JSON, YAML) and storing them as secrets in the SysBot cache.
Useful for managing test data and configuration files.
"""
import csv
import json
import yaml

from sysbot.utils.engine import ComponentBase


class Data(ComponentBase):
    """
    Data loader plugin for managing test data from various file formats.
    
    This class provides methods to load data from CSV, JSON, and YAML files
    and optionally store them in the SysBot secrets cache.
    """
    
    def csv(self, file: str, key: str = None) -> list[dict]:
        """
        Load CSV file and optionally store in secrets cache.
        
        Args:
            file: Path to the CSV file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            List of dictionaries representing CSV rows if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the CSV file does not exist.
            RuntimeError: If there's an error reading or parsing the CSV file.
        """
        file_path = file
        try:
            result = []
            with open(file_path, mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    result.append(row)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        except csv.Error as e:
            raise RuntimeError(f"Error reading CSV file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading CSV: {e}")

    def json(self, file: str, key: str = None) -> dict:
        """
        Load JSON file and optionally store in secrets cache.
        
        Args:
            file: Path to the JSON file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            Dictionary containing JSON data if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the JSON file does not exist.
            RuntimeError: If there's an error reading or parsing the JSON file.
        """
        file_path = file
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                result = json.load(file)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"JSON file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading JSON: {e}")

    def yaml(self, file: str, key: str = None) -> dict:
        """
        Load YAML file and optionally store in secrets cache.
        
        Args:
            file: Path to the YAML file to load.
            key: Optional key to store the data in secrets cache.
                If provided, returns "Imported", otherwise returns the data.
        
        Returns:
            Dictionary containing YAML data if key is None,
            otherwise returns "Imported" string after storing in cache.
        
        Raises:
            FileNotFoundError: If the YAML file does not exist.
            RuntimeError: If there's an error reading or parsing the YAML file.
        """
        file_path = file
        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                result = yaml.safe_load(file)
            if key is not None:
                self._sysbot._cache.secrets.register(key, result)
                return "Imported"
            else:
                return result
        except FileNotFoundError:
            raise FileNotFoundError(f"YAML file not found: {file_path}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML file: {file_path} - {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error occurred while loading YAML: {e}")
