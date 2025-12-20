*** Settings ***
Name           vmware.nsx

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        443

*** Keywords ***

Init test suite
    # Note: This test suite requires a valid NSX Manager connection
    # Configure your NSX Manager credentials in tests/.dataset/connexion.yml
    # Example format:
    # nsx:
    #   host: "nsx-manager.example.com"
    #   username: "admin"
    #   password: "password"
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    # Open HTTPS session with basicauth to NSX Manager
    Open Session    nsx    https    basicauth    connexion.nsx.host    ${PORT}   connexion.nsx.username    connexion.nsx.password    is_secret=True

*** Test Cases ***

Get Logical Switches
    ${output}=    Call Components    modules.vmware.nsx.get_logical_switches    nsx
    Should Be List    ${output}
    Log    Logical Switches: ${output}

Get Logical Routers
    ${output}=    Call Components    modules.vmware.nsx.get_logical_routers    nsx
    Should Be List    ${output}
    Log    Logical Routers: ${output}

Get Transport Zones
    ${output}=    Call Components    modules.vmware.nsx.get_transport_zones    nsx
    Should Be List    ${output}
    Log    Transport Zones: ${output}

Get Edge Clusters
    ${output}=    Call Components    modules.vmware.nsx.get_edge_clusters    nsx
    Should Be List    ${output}
    Log    Edge Clusters: ${output}

Get Firewall Sections
    ${output}=    Call Components    modules.vmware.nsx.get_firewall_sections    nsx
    Should Be List    ${output}
    Log    Firewall Sections: ${output}

Get Firewall Rules
    ${output}=    Call Components    modules.vmware.nsx.get_firewall_rules    nsx
    Should Be List    ${output}
    Log    Firewall Rules: ${output}

Get Security Groups
    ${output}=    Call Components    modules.vmware.nsx.get_security_groups    nsx
    Should Be List    ${output}
    Log    Security Groups: ${output}

Get IP Pools
    ${output}=    Call Components    modules.vmware.nsx.get_ip_pools    nsx
    Should Be List    ${output}
    Log    IP Pools: ${output}

Get Controllers
    ${output}=    Call Components    modules.vmware.nsx.get_controllers    nsx
    Should Be List    ${output}
    Log    Controllers: ${output}

Get Version
    ${output}=    Call Components    modules.vmware.nsx.get_version    nsx
    Should Be Equal As Strings    ${{type($output).__name__}}    dict
    Log    Version Info: ${output}
