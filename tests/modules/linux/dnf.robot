*** Settings ***
Name           Fonctionnal tests linux for dnf module

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${IP}=          192.168.1.112
${PORT}=        22
${USER}=        sysbot
${PASSWORD}=    P@ssw0rd

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Open Session    target    ssh    bash    ${IP}    ${PORT}   ${USER}    ${PASSWORD}

*** Test Cases ***

repolist method works
    ${output}=    Call Module    modules.linux.dnf.repolist    target
    Should Not Be Empty    ${output}[0][name]

repofile method works
    ${output}=    Call Module    modules.linux.dnf.repofile    target    /etc/yum.repos.d/fedora.repo
    Should Be Equal    ${output}[fedora][enabled]    1
