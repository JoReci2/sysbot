*** Settings ***
Name           linux.libvirt

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***

version method works
    ${output}=    Call Components    modules.linux.libvirt.version    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Compiled against library

nodeinfo method works
    ${output}=    Call Components    modules.linux.libvirt.nodeinfo    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    CPU model

list method works
    ${output}=    Call Components    modules.linux.libvirt.list    target
    Should Not Be Empty    ${output}

domstate method works with existing domain
    ${domains}=    Call Components    modules.linux.libvirt.list    target
    ${domain}=    Get From List    ${domains}    0
    ${output}=    Call Components    modules.linux.libvirt.domstate    target    ${domain}
    Should Not Be Empty    ${output}

dominfo method works with existing domain
    ${domains}=    Call Components    modules.linux.libvirt.list    target
    ${domain}=    Get From List    ${domains}    0
    ${output}=    Call Components    modules.linux.libvirt.dominfo    target    ${domain}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    State

pool_list method works
    ${output}=    Call Components    modules.linux.libvirt.pool_list    target
    Should Not Be Empty    ${output}

pool_info method works with existing pool
    ${pools}=    Call Components    modules.linux.libvirt.pool_list    target
    ${pool}=    Get From List    ${pools}    0
    ${output}=    Call Components    modules.linux.libvirt.pool_info    target    ${pool}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    State

net_list method works
    ${output}=    Call Components    modules.linux.libvirt.net_list    target
    Should Not Be Empty    ${output}

net_info method works with existing network
    ${networks}=    Call Components    modules.linux.libvirt.net_list    target
    ${network}=    Get From List    ${networks}    0
    ${output}=    Call Components    modules.linux.libvirt.net_info    target    ${network}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Active
