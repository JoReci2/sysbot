*** Settings ***
Name           Fonctionnal tests linux for rpm module

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${IP}=          192.168.1.112
${PORT}=        22
${USER}=        thibault.scire
${PASSWORD}=    Viv3_L3s_B00bs

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Open Session    target    ssh    bash    ${IP}    ${PORT}   ${USER}    ${PASSWORD}

*** Test Cases ***

is_installed method works
    ${output}=    Call Module    linux.rpm.is_installed    target    openssh
    Should Be Equal    ${output}    0

version method works
    ${output}=    Call Module    linux.rpm.version    target    openssh
    Should Not Be Empty    ${output}
    Log To Console    ${output}

release method works
    ${output}=    Call Module    linux.rpm.release    target    openssh
    Should Not Be Empty    ${output}
    Log To Console    ${output}