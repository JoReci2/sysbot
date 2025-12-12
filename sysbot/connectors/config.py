"""
Connector configuration and constants.
Defines default ports and standard response formats for all connectors.
"""

# Default ports for each protocol
DEFAULT_PORTS = {
    "ssh": 22,
    "winrm": 5986,  # HTTPS WinRM
    "http": 80,
    "https": 443,
    "socket": None,  # Socket requires explicit port
}


def create_response(status_code=0, result=None, error=None, metadata=None):
    """
    Create a standardized response format for all connectors.
    
    Args:
        status_code (int): Status code (0 = success, non-zero = error)
        result: The result data from the command execution
        error (str): Error message if any
        metadata (dict): Additional metadata about the execution
    
    Returns:
        dict: Standardized response with StatusCode, Result, Error, and Metadata
    """
    response = {
        "StatusCode": status_code,
        "Result": result,
        "Error": error,
        "Metadata": metadata or {}
    }
    return response
