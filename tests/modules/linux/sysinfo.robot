*** Settings ***
Name           Fonctionnal tests linux for systeminfo module

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
os_release method works
    ${output}=    Call Module    linux.sysinfo.os_release    target    
    Should Be Equal    ${output}[NAME]        Fedora Linux

hostname method works
    ${output}=    Call Module    linux.sysinfo.hostname    target
    Should Be Equal    ${output}        lab01

uptime method works
    ${output}=    Call Module    linux.sysinfo.uptime    target
    Should Contain    ${output}    days

kernel method works
    ${output}=    Call Module    linux.sysinfo.kernel    target
    Should Contain    ${output}    6.15.9    

architecture method works
    ${output}=    Call Module    linux.sysinfo.architecture    target
    Should Be Equal    ${output}    x86_64

ram method works
    ${output}=    Call Module    linux.sysinfo.ram    target
    Should Be Equal    ${output}[used]    15Gi

cpu method works
    ${output}=    Call Module    linux.sysinfo.cpu    target
    Should Be Equal    ${output}[Architecture]    x86_64