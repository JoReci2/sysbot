from sysbot.Sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

# Open an HTTP session with basic authentication
bot.open_session(
    alias="my_api",
    protocol="http",
    product="basicauth",
    host="api.example.com",
    port=443,
    login="api_user",
    password="api_password"
)

# Perform a GET request
result = bot.execute_command("my_api", "GET", endpoint="/users")
print(result)

# Close the session
bot.close_session("my_api")
