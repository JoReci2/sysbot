#!/usr/bin/env python3
"""
Basic example of using SysBot with local bash execution.
This example demonstrates how to execute bash commands locally
without requiring an SSH connection.
"""

from sysbot.Sysbot import Sysbot

# Initialize SysBot (load no modules to avoid module errors)
bot = Sysbot([])

# Open a local bash session
# Note: host and port are required by the API but not used for local execution
bot.open_session(
    alias="local_bash",
    protocol="local",
    product="bash",
    host="localhost",
    port=0
)

# Execute a simple command
result = bot.execute_command("local_bash", "echo 'Hello from local bash'")
print("Output:", result)

# Get current directory
result = bot.execute_command("local_bash", "pwd")
print("Current directory:", result)

# List files
result = bot.execute_command("local_bash", "ls -la")
print("Files:\n", result)

# Close the session
bot.close_session("local_bash")
