*** Settings ***
Name           linux.firewalld

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
getZones method works
    ${output}=    Call Components    modules.linux.firewalld.getZones    target
    Should Contain    ${output}    public

getActiveZones method works
    ${output}=    Call Components    modules.linux.firewalld.getActiveZones    target
    Should Be Equal    ${output}[public (default)][0]    enp1s0

getDefaultZone method works
    ${output}=    Call Components    modules.linux.firewalld.getDefaultZone    target
    Should Be Equal    ${output}    public

getForwardPorts method works
    ${output}=    Call Components    modules.linux.firewalld.getForwardPorts    target    public    runas=True
    Should Not Contain    ${output}    22:tcp:listen

getPorts method works
    ${output}=    Call Components    modules.linux.firewalld.getPorts    target    public    runas=True
    Should Contain    ${output}    25565/tcp

getInterface method works
    ${output}=    Call Components    modules.linux.firewalld.getInterface    target    public    runas=True
    Should Contain    ${output}    enp1s0

getServices method works
    ${output}=    Call Components    modules.linux.firewalld.getServices    target    public    runas=True
    Should Contain    ${output}    ssh

getProtocols method works
    ${output}=    Call Components    modules.linux.firewalld.getProtocols    target    public    runas=True
    Should Not Contain    ${output}    ipv4

getSourcePorts method works
    ${output}=    Call Components    modules.linux.firewalld.getSourcePorts    target    public    runas=True
    Should NotContain    ${output}    22:tcp:listen

getSources method works
    ${output}=    Call Components    modules.linux.firewalld.getSources    target    public    runas=True
    Should Not Contain    ${output}    10.0.0.0/8