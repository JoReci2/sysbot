*** Settings ***
Name           vmware.vsphere

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        443

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    vcenter    http    vsphere    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Test Cases ***

list_vms method works
    ${output}=    Call Components    modules.vmware.vsphere.list_vms    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

list_hosts method works
    ${output}=    Call Components    modules.vmware.vsphere.list_hosts    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

list_datastores method works
    ${output}=    Call Components    modules.vmware.vsphere.list_datastores    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

list_clusters method works
    ${output}=    Call Components    modules.vmware.vsphere.list_clusters    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

list_networks method works
    ${output}=    Call Components    modules.vmware.vsphere.list_networks    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

list_datacenters method works
    ${output}=    Call Components    modules.vmware.vsphere.list_datacenters    vcenter
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

get_vm method works with existing vm
    ${vms}=    Call Components    modules.vmware.vsphere.list_vms    vcenter
    ${vm}=    Get From List    ${vms}    0
    ${vm_id}=    Get From Dictionary    ${vm}    vm
    ${output}=    Call Components    modules.vmware.vsphere.get_vm    vcenter    ${vm_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name

get_vm_power_state method works with existing vm
    ${vms}=    Call Components    modules.vmware.vsphere.list_vms    vcenter
    ${vm}=    Get From List    ${vms}    0
    ${vm_id}=    Get From Dictionary    ${vm}    vm
    ${output}=    Call Components    modules.vmware.vsphere.get_vm_power_state    vcenter    ${vm_id}
    Should Not Be Empty    ${output}
    Should Match Regexp    ${output}    POWERED_(ON|OFF|SUSPENDED)

get_host method works with existing host
    ${hosts}=    Call Components    modules.vmware.vsphere.list_hosts    vcenter
    ${host}=    Get From List    ${hosts}    0
    ${host_id}=    Get From Dictionary    ${host}    host
    ${output}=    Call Components    modules.vmware.vsphere.get_host    vcenter    ${host_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name

get_datastore method works with existing datastore
    ${datastores}=    Call Components    modules.vmware.vsphere.list_datastores    vcenter
    ${datastore}=    Get From List    ${datastores}    0
    ${ds_id}=    Get From Dictionary    ${datastore}    datastore
    ${output}=    Call Components    modules.vmware.vsphere.get_datastore    vcenter    ${ds_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name

get_cluster method works with existing cluster
    ${clusters}=    Call Components    modules.vmware.vsphere.list_clusters    vcenter
    ${cluster}=    Get From List    ${clusters}    0
    ${cluster_id}=    Get From Dictionary    ${cluster}    cluster
    ${output}=    Call Components    modules.vmware.vsphere.get_cluster    vcenter    ${cluster_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name

get_network method works with existing network
    ${networks}=    Call Components    modules.vmware.vsphere.list_networks    vcenter
    ${network}=    Get From List    ${networks}    0
    ${network_id}=    Get From Dictionary    ${network}    network
    ${output}=    Call Components    modules.vmware.vsphere.get_network    vcenter    ${network_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name

get_datacenter method works with existing datacenter
    ${datacenters}=    Call Components    modules.vmware.vsphere.list_datacenters    vcenter
    ${datacenter}=    Get From List    ${datacenters}    0
    ${dc_id}=    Get From Dictionary    ${datacenter}    datacenter
    ${output}=    Call Components    modules.vmware.vsphere.get_datacenter    vcenter    ${dc_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name
