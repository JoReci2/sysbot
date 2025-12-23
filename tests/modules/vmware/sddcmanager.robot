*** Settings ***
Name           vmware.sddcmanager

Library        Collections
Library        sysbot.Sysbot

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}    connexion.username    connexion.password    is_secret=True

*** Test Cases ***
get_hosts method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_hosts    target
    Should Be True    isinstance($output, list)

get_host method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_host    target    test-host-id
    Should Be True    isinstance($output, dict)

get_domains method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_domains    target
    Should Be True    isinstance($output, list)

get_domain method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_domain    target    test-domain
    Should Be True    isinstance($output, dict)

get_clusters method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_clusters    target
    Should Be True    isinstance($output, list)

get_cluster method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_cluster    target    test-cluster-id
    Should Be True    isinstance($output, dict)

get_vcenters method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_vcenters    target
    Should Be True    isinstance($output, list)

get_vcenter method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_vcenter    target    test-vcenter-id
    Should Be True    isinstance($output, dict)

get_nsxt_clusters method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_nsxt_clusters    target
    Should Be True    isinstance($output, list)

get_nsxt_cluster method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_nsxt_cluster    target    test-nsxt-cluster-id
    Should Be True    isinstance($output, dict)

get_credentials method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_credentials    target
    Should Be True    isinstance($output, list)

get_sddc_manager method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_sddc_manager    target
    Should Be True    isinstance($output, dict)

get_tasks method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_tasks    target
    Should Be True    isinstance($output, list)

get_task method works
    ${output}=    Call Components    modules.vmware.sddcmanager.get_task    target    test-task-id
    Should Be True    isinstance($output, dict)
