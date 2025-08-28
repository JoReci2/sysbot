*** Settings ***
Name           Fonctionnal tests linux for systemd module

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

is_active method works
    ${output}=    Call Module    linux.systemd.is_active    target    sshd
    Should Be Equal    ${output}    active


is_enabled method works
    ${output}=    Call Module    linux.systemd.is_enabled    target    sshd
    Should Be Equal    ${output}    enabled

is_failed method works
    ${output}=    Call Module    linux.systemd.is_failed    target    sshd
    Should Be Equal    ${output}    active