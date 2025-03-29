"""
MIT License

Copyright (c) 2024 Thibault SCIRE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from robot.output.listeners import Listeners
import yaml
import requests

class http(object):
    """
    A custom listener for Robot Framework that collects test results.
    """

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, config_file=None):
        """
        Initializes the Listener.
        config_file need to be format :
        project:
            name: test
            version: 0.0.1
        server:
            url: http://localhost:5000/api/v1/test_results
            login: admin
            password: admin
            
        """
        self.config = self.__load_config__(config_file)

    def __load_config__(self, config_file: str) -> dict:
        """
        Load the configuration file.
        """
        if not config_file:
            raise Exception("Configuration file path is required.")

        try:
            with open(config_file, 'r') as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
                if not isinstance(config, dict):  # Vérifie que le contenu est bien un dict
                    raise Exception("Invalid YAML format: expected a dictionary.")
                
                # Vérification des clés attendues
                if "project" not in config or "server" not in config:
                    raise Exception("Invalid configuration file: missing 'project' or 'server' section.")
                if "name" not in config["project"] or "version" not in config["project"]:
                    raise Exception("Invalid configuration file: missing 'name' or 'version' in 'project'.")
                if "url" not in config["server"] or "login" not in config["server"] or "password" not in config["server"]:
                    raise Exception("Invalid configuration file: missing required fields in 'server'.")

                return config
        except FileNotFoundError:
            raise Exception(f"Configuration file '{config_file}' not found.")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML file: {e}")
        except Exception as e:
            raise Exception(f"Error loading config file: {e}")
            
    def start_suite(self, name, attributes):
        """
        Handles the start of a test suite and captures its name.
        """
        self.suite_name = attributes.name
        self.suite_source = attributes.source
        #self.suite_tags = attributes.tags

    def end_test(self, name, attributes):
        """
        Handles the end of a test and collects its results.
        """
        try:
            requests.post(
                url=self.config['server']['url'],
                json={
                    'project': self.config['project']['name'],
                    'version': self.config['project']['version'],
                    'test_suite_name': self.suite_name,
                    'test_suite_source': self.suite_source,
                    'test_suite_tags': self.suite_tags,
                    'test_case_name': attributes.name,
                    'test_case_result': attributes.status,
                    'test_case_message': attributes.message,
                    'test_case_tags': attributes.tags
                },
                auth=(self.config['server']['login'], self.config['server']['password'])
            )
        except Exception as e:
            raise Exception(f"Error inserting test result: {e}")
