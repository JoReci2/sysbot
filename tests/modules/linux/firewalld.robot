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
    Should Not Be Empty    ${zones}

getActiveZones method works
    ${output}=    Call Components    modules.linux.firewalld.getActiveZones    target
    Should Not Be Empty    ${active_zones}