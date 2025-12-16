from sysbot.Sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

# Open a WinRM session to a Windows system
bot.open_session(
    alias="my_windows_server",
    protocol="winrm",
    product="powershell",
    host="192.168.1.200",
    port=5986,
    login="administrator",
    password="password"
)

# Execute a PowerShell command
result = bot.execute_command("my_windows_server", "Get-Process")
print(result)

# Close the session
bot.close_session("my_windows_server")
