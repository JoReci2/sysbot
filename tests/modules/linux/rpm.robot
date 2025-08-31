*** Settings ***
Name           linux.rpm

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    connexion    tests/.dataset/connexion.yml    is_secret=True
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***

is_installed method works
    ${output}=    Call Components    modules.linux.rpm.is_installed    target    openssh
    Should Be Equal    ${output}    0

version method works
    ${output}=    Call Components    modules.linux.rpm.version    target    openssh
    Should Not Be Empty    ${output}
    Log To Console    ${output}

release method works
    ${output}=    Call Components    modules.linux.rpm.release    target    openssh
    Should Not Be Empty    ${output}
    Log To Console    ${output}