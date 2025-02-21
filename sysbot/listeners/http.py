from robot.output.listeners import Listeners
import yaml
import requests

class Listener:
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
        try:
            with open(config_file, 'r') as file:
                return yaml.load(file, Loader=yaml.FullLoader)
        except Exception as e:
            log.error(f"Error loading config file: {e}")

    def start_suite(self, name, attributes):
        """
        Handles the start of a test suite and captures its name.
        """
        log.info(f"Starting test suite: {name}")
        self.suite_name = attributes.name
        self.suite_source = attributes.source
        self.suite_tags = attributes.tags

    def end_test(self, name, attributes):
        """
        Handles the end of a test and collects its results.
        """
        log.info(f"Ending test: {name} with status {attributes.status}")
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
            log.error(f"Error inserting test result: {e}")
