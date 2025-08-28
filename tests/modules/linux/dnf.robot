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
    ${output}=    Call Module    linux.dnf.repolist    target
    Should Be Equal    ${output}[0][name]    Fedora 42 - x86_64 - Updates

repofile method works
    ${output}=    Call Module    linux.dnf.repofile    target    /etc/yum.repos.d/fedora.repo
    Should Be Equal    ${output}[fedora][enabled]    1
