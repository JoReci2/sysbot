*** Settings ***
Name           linux.systeminfo

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
os_release method works
    ${output}=    Call Components    modules.linux.sysinfo.os_release    target    
    Should Be Equal    ${output}[NAME]        Fedora Linux

hostname method works
    ${output}=    Call Components    modules.linux.sysinfo.hostname    target
    Should Be Equal    ${output}        lab01

fqdn method works
    ${output}=    Call Components    modules.linux.sysinfo.fqdn    target
    Should Be Equal    ${output}        lab01

domain method works
    ${output}=    Call Components    modules.linux.sysinfo.domain    target
    Should Be Empty    ${output}

uptime method works
    ${output}=    Call Components    modules.linux.sysinfo.uptime    target
    Should Contain    ${output}    minutes

kernel method works
    ${output}=    Call Components    modules.linux.sysinfo.kernel    target
    Should Contain    ${output}    6.15.9    

architecture method works
    ${output}=    Call Components    modules.linux.sysinfo.architecture    target
    Should Be Equal    ${output}    x86_64

ram method works
    ${output}=    Call Components    modules.linux.sysinfo.ram    target
    Should Be Equal    ${output}[used]    15Gi

cpu method works
    ${output}=    Call Components    modules.linux.sysinfo.cpu    target
    Should Be Equal    ${output}[Architecture]    x86_64

keyboard method works
    ${output}=    Call Components    modules.linux.sysinfo.keyboard    target
    Should Be Equal    ${output}    fr

timezone method works
    ${output}=    Call Components    modules.linux.sysinfo.timezone    target
    Should Contain    ${output}    Etc/UTC