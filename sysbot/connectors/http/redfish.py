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

import redfish as RedfishLibrary
import json

class Redfish(object):
    """
    This class provides methods for interacting with systems using the Redfish API.
    It uses the redfish library to establish and manage sessions.
    """

    def open_session(self, host, port, login, password):
        """
        Opens a session to a system using the Redfish API.
        """
        try:
            client = RedfishLibrary.redfish_client(base_url=f"https://{host}:{port}", username=login, password=password, default_prefix='/redfish/v1/')
            client.login(auth="session")
            return client
        except Exception as e:
            raise Exception(f"Failed to open session: {str(e)}")

    def execute_command(self, session, command, options):
        """
        Sends a GET request to a system using the Redfish API.
        """
        try:
            response = session.get(command)
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to execute command: {str(e)}")

    def close_session(self, session):
        """
        Closes the session to the Redfish API.
        """
        try:
            session.logout()
        except Exception as e:
            raise Exception(f"Failed to close session: {str(e)}")