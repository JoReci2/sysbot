*** Settings ***
Name           linux.kubernetes

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        22
${NAMESPACE}=   default

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Test Cases ***
version method works
    ${output}=    Call Components    modules.linux.kubernetes.version    target    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    clientVersion

cluster_info method works
    ${output}=    Call Components    modules.linux.kubernetes.cluster_info    target    runas=True
    Should Not Be Empty    ${output}
    Should Contain    ${output}    Kubernetes

get_nodes method works
    ${output}=    Call Components    modules.linux.kubernetes.get_nodes    target    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_namespaces method works
    ${output}=    Call Components    modules.linux.kubernetes.get_namespaces    target    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_namespace method works
    ${output}=    Call Components    modules.linux.kubernetes.get_namespace    target    ${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    metadata

get_pods method works
    ${output}=    Call Components    modules.linux.kubernetes.get_pods    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_services method works
    ${output}=    Call Components    modules.linux.kubernetes.get_services    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_deployments method works
    ${output}=    Call Components    modules.linux.kubernetes.get_deployments    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_configmaps method works
    ${output}=    Call Components    modules.linux.kubernetes.get_configmaps    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items

get_secrets method works
    ${output}=    Call Components    modules.linux.kubernetes.get_secrets    target    namespace=${NAMESPACE}    runas=True
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    items
