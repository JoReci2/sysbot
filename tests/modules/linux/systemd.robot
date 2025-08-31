*** Settings ***
Name           linux.systemd

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

is_active method works
    ${output}=    Call Components    modules.linux.systemd.is_active    target    sshd
    Should Be Equal    ${output}    active


is_enabled method works
    ${output}=    Call Components    modules.linux.systemd.is_enabled    target    sshd
    Should Be Equal    ${output}    enabled

is_failed method works
    ${output}=    Call Components    modules.linux.systemd.is_failed    target    sshd
    Should Be Equal    ${output}    active