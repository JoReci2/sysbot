from sysbot.Sysbot import Sysbot

# Créer une instance SysBot
bot = Sysbot()

# Ouvrir une session vers vCenter Server
bot.open_session(
    alias="vcenter",
    protocol="http",
    product="vsphere",
    host="vcenter.example.com",
    port=443,
    login="administrator@vsphere.local",
    password="votre-mot-de-passe"
)

# Lister toutes les machines virtuelles
vms = bot.execute_command("vcenter", "/rest/vcenter/vm", options={"method": "GET"})
print("Machines Virtuelles:", vms)

# Lister tous les hôtes
hosts = bot.execute_command("vcenter", "/rest/vcenter/host", options={"method": "GET"})
print("Hôtes ESXi:", hosts)

# Lister tous les datastores
datastores = bot.execute_command("vcenter", "/rest/vcenter/datastore", options={"method": "GET"})
print("Datastores:", datastores)

# Fermer la session
bot.close_session("vcenter")


# Utilisation du module vmware.vsphere (lorsqu'il est chargé)
# Cela nécessite de charger le module: bot = Sysbot("vmware.vsphere")
# Ou avec tous les modules chargés: bot = Sysbot()

# Ensuite, vous pouvez utiliser les méthodes du module directement:
# vms = bot.vmware.vsphere.list_vms("vcenter")
# vm_details = bot.vmware.vsphere.get_vm("vcenter", "vm-123")
# power_state = bot.vmware.vsphere.get_vm_power_state("vcenter", "vm-123")
# hosts = bot.vmware.vsphere.list_hosts("vcenter")
# datastores = bot.vmware.vsphere.list_datastores("vcenter")
