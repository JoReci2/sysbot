from sysbot.Sysbot import Sysbot

# Créer une instance SysBot
bot = Sysbot()

# Exemple 1: Authentification Basic
bot.open_session(
    alias="mon_api",
    protocol="http",
    product="basicauth",
    host="api.exemple.com",
    port=443,
    login="utilisateur_api",
    password="mot_de_passe_api"
)

# Effectuer une requête GET
result = bot.execute_command("mon_api", "/utilisateurs", options={"method": "GET"})
print(result)

# Effectuer une requête POST avec des données JSON
result = bot.execute_command(
    "mon_api",
    "/utilisateurs",
    options={
        "method": "POST",
        "json": {"nom": "Jean Dupont", "email": "jean@exemple.com"}
    }
)
print(result)

# Fermer la session
bot.close_session("mon_api")


# Exemple 2: Authentification par clé API
bot.open_session(
    alias="mon_api_cle",
    protocol="http",
    product="apikey",
    host="api.exemple.com",
    port=443,
    api_key="votre-cle-api-ici",
    api_key_header="X-API-Key"
)

result = bot.execute_command("mon_api_cle", "/donnees", options={"method": "GET"})
print(result)

bot.close_session("mon_api_cle")


# Exemple 3: Authentification OAuth 2.0
bot.open_session(
    alias="mon_oauth2",
    protocol="http",
    product="oauth2",
    host="api.exemple.com",
    port=443,
    client_id="votre-client-id",
    client_secret="votre-client-secret",
    access_token="votre-access-token"
)

result = bot.execute_command("mon_oauth2", "/protege", options={"method": "GET"})
print(result)

bot.close_session("mon_oauth2")


# Exemple 4: Authentification JWT
bot.open_session(
    alias="mon_jwt",
    protocol="http",
    product="jwt",
    host="api.exemple.com",
    port=443,
    login="utilisateur@exemple.com",
    secret_key="votre-cle-secrete",
    algorithm="HS256"
)

result = bot.execute_command("mon_jwt", "/securise", options={"method": "GET"})
print(result)

bot.close_session("mon_jwt")


# Exemple 5: Authentification par certificat
bot.open_session(
    alias="mon_cert",
    protocol="http",
    product="certificate",
    host="api.exemple.com",
    port=443,
    cert_file="/chemin/vers/client.crt",
    key_file="/chemin/vers/client.key"
)

result = bot.execute_command("mon_cert", "/securise", options={"method": "GET"})
print(result)

bot.close_session("mon_cert")

