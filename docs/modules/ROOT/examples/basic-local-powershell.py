#!/usr/bin/env python3
"""
Basic example of using SysBot with local PowerShell execution.
This example demonstrates how to execute PowerShell commands locally
without requiring an SSH or WinRM connection.
"""

from sysbot.Sysbot import Sysbot

# Initialize SysBot (load no modules to avoid module errors)
bot = Sysbot([])

# Open a local PowerShell session
# Note: host and port are required by the API but not used for local execution
bot.open_session(
    alias="local_ps",
    protocol="local",
    product="powershell",
    host="localhost",
    port=0
)

# Execute a simple command
result = bot.execute_command("local_ps", "Write-Output 'Hello from local PowerShell'")
print("Output:", result)

# Get current date/time
result = bot.execute_command("local_ps", "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'")
print("Current date/time:", result)

# Get PowerShell version
result = bot.execute_command("local_ps", "$PSVersionTable.PSVersion")
print("PowerShell version:\n", result)

# Close the session
bot.close_session("local_ps")
