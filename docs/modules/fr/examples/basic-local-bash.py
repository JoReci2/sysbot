#!/usr/bin/env python3
"""
Exemple de base d'utilisation de SysBot avec l'exécution bash locale.
Cet exemple démontre comment exécuter des commandes bash localement
sans nécessiter de connexion SSH.
"""

from sysbot.Sysbot import Sysbot

# Initialiser SysBot (ne charge aucun module pour éviter les erreurs de module)
bot = Sysbot([])

# Ouvrir une session bash locale
# Note: host et port sont requis par l'API mais ne sont pas utilisés pour l'exécution locale
bot.open_session(
    alias="local_bash",
    protocol="local",
    product="bash",
    host="localhost",
    port=0
)

# Exécuter une commande simple
result = bot.execute_command("local_bash", "echo 'Bonjour depuis bash local'")
print("Sortie:", result)

# Obtenir le répertoire courant
result = bot.execute_command("local_bash", "pwd")
print("Répertoire courant:", result)

# Lister les fichiers
result = bot.execute_command("local_bash", "ls -la")
print("Fichiers:\n", result)

# Fermer la session
bot.close_session("local_bash")
