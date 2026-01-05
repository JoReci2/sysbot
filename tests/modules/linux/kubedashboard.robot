*** Settings ***
Name           linux.kubedashboard

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        22
${NAMESPACE}=   kubernetes-dashboard

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Test Cases ***
get_dashboard_deployment method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_deployment    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    metadata
    Dictionary Should Contain Key    ${output}    spec

get_dashboard_service method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_service    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    metadata
    Dictionary Should Contain Key    ${output}    spec

get_dashboard_pods method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_pods    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_dashboard_namespace method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_namespace    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    metadata
    Dictionary Should Contain Key    ${output}    status

get_dashboard_serviceaccount method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_serviceaccount    target    name=kubernetes-dashboard    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    metadata

get_dashboard_secrets method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_secrets    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_dashboard_configmaps method works
    ${output}=    Call Components    modules.linux.kubedashboard.get_dashboard_configmaps    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

check_dashboard_status method works
    ${output}=    Call Components    modules.linux.kubedashboard.check_dashboard_status    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    name
    Dictionary Should Contain Key    ${output}    namespace
    Dictionary Should Contain Key    ${output}    replicas
