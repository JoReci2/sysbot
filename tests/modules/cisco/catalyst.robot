*** Settings ***
Name           cisco.catalyst

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    catalyst_switch    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***
version method works
    ${output}=    Call Components    modules.cisco.catalyst.version    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

hostname method works
    ${output}=    Call Components    modules.cisco.catalyst.hostname    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

uptime method works
    ${output}=    Call Components    modules.cisco.catalyst.uptime    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

interfaces method works
    ${output}=    Call Components    modules.cisco.catalyst.interfaces    catalyst_switch
    Should Not Be Empty    ${output}
    Should Contain    ${output}    Interface
    Log    ${output}

vlans method works
    ${output}=    Call Components    modules.cisco.catalyst.vlans    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

vlan_exists method works for VLAN 1
    ${output}=    Call Components    modules.cisco.catalyst.vlan_exists    catalyst_switch    1
    Should Be True    ${output}

running_config method works
    ${output}=    Call Components    modules.cisco.catalyst.running_config    catalyst_switch
    Should Not Be Empty    ${output}
    Should Contain    ${output}    version
    Log    ${output}

mac_address_table method works
    ${output}=    Call Components    modules.cisco.catalyst.mac_address_table    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

arp_table method works
    ${output}=    Call Components    modules.cisco.catalyst.arp_table    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

spanning_tree method works
    ${output}=    Call Components    modules.cisco.catalyst.spanning_tree    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

cdp_neighbors method works
    ${output}=    Call Components    modules.cisco.catalyst.cdp_neighbors    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

inventory method works
    ${output}=    Call Components    modules.cisco.catalyst.inventory    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}

log method works
    ${output}=    Call Components    modules.cisco.catalyst.log    catalyst_switch
    Should Not Be Empty    ${output}
    Log    ${output}
