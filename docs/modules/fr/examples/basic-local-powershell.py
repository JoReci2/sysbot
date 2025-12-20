#!/usr/bin/env python3
"""
Exemple de base d'utilisation de SysBot avec l'exécution PowerShell locale.
Cet exemple démontre comment exécuter des commandes PowerShell localement
sans nécessiter de connexion SSH ou WinRM.
"""

from sysbot.Sysbot import Sysbot

# Initialiser SysBot
bot = Sysbot()

# Ouvrir une session PowerShell locale
# Note: host et port sont requis par l'API mais ne sont pas utilisés pour l'exécution locale
bot.open_session(
    alias="local_ps",
    protocol="local",
    product="powershell",
    host="localhost",
    port=0
)

# Exécuter une commande simple
result = bot.execute_command("local_ps", "Write-Output 'Bonjour depuis PowerShell local'")
print("Sortie:", result)

# Obtenir la date/heure actuelle
result = bot.execute_command("local_ps", "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'")
print("Date/heure actuelle:", result)

# Obtenir la version de PowerShell
result = bot.execute_command("local_ps", "$PSVersionTable.PSVersion")
print("Version de PowerShell:\n", result)

# Fermer la session
bot.close_session("local_ps")
