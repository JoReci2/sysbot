from sysbot.Sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

# Example 1: Basic Authentication
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
result = bot.execute_command("my_api", "/users", options={"method": "GET"})
print(result)

# Perform a POST request with JSON data
result = bot.execute_command(
    "my_api",
    "/users",
    options={
        "method": "POST",
        "json": {"name": "John Doe", "email": "john@example.com"}
    }
)
print(result)

# Close the session
bot.close_session("my_api")


# Example 2: API Key Authentication
bot.open_session(
    alias="my_api_key",
    protocol="http",
    product="apikey",
    host="api.example.com",
    port=443,
    api_key="your-api-key-here",
    api_key_header="X-API-Key"
)

result = bot.execute_command("my_api_key", "/data", options={"method": "GET"})
print(result)

bot.close_session("my_api_key")


# Example 3: OAuth 2.0 Authentication
bot.open_session(
    alias="my_oauth2",
    protocol="http",
    product="oauth2",
    host="api.example.com",
    port=443,
    client_id="your-client-id",
    client_secret="your-client-secret",
    access_token="your-access-token"
)

result = bot.execute_command("my_oauth2", "/protected", options={"method": "GET"})
print(result)

bot.close_session("my_oauth2")


# Example 4: JWT Authentication
bot.open_session(
    alias="my_jwt",
    protocol="http",
    product="jwt",
    host="api.example.com",
    port=443,
    login="user@example.com",
    secret_key="your-secret-key",
    algorithm="HS256"
)

result = bot.execute_command("my_jwt", "/secure", options={"method": "GET"})
print(result)

bot.close_session("my_jwt")


# Example 5: Certificate Authentication
bot.open_session(
    alias="my_cert",
    protocol="http",
    product="certificate",
    host="api.example.com",
    port=443,
    cert_file="/path/to/client.crt",
    key_file="/path/to/client.key"
)

result = bot.execute_command("my_cert", "/secure", options={"method": "GET"})
print(result)

bot.close_session("my_cert")

