from sysbot.Sysbot import Sysbot

# Create a SysBot instance
bot = Sysbot()

# Open a session to vCenter Server
bot.open_session(
    alias="vcenter",
    protocol="http",
    product="vsphere",
    host="vcenter.example.com",
    port=443,
    login="administrator@vsphere.local",
    password="your-password"
)

# List all virtual machines
vms = bot.execute_command("vcenter", "/rest/vcenter/vm", options={"method": "GET"})
print("Virtual Machines:", vms)

# List all hosts
hosts = bot.execute_command("vcenter", "/rest/vcenter/host", options={"method": "GET"})
print("ESXi Hosts:", hosts)

# List all datastores
datastores = bot.execute_command("vcenter", "/rest/vcenter/datastore", options={"method": "GET"})
print("Datastores:", datastores)

# Close the session
bot.close_session("vcenter")


# Using the vmware.vsphere module (when loaded)
# This requires loading the module: bot = Sysbot("vmware.vsphere")
# Or with all modules loaded: bot = Sysbot()

# Then you can use the module methods directly:
# vms = bot.vmware.vsphere.list_vms("vcenter")
# vm_details = bot.vmware.vsphere.get_vm("vcenter", "vm-123")
# power_state = bot.vmware.vsphere.get_vm_power_state("vcenter", "vm-123")
# hosts = bot.vmware.vsphere.list_hosts("vcenter")
# datastores = bot.vmware.vsphere.list_datastores("vcenter")
