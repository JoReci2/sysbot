*** Settings ***
Name           linux.users

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
name method works
    ${output}=    Call Components    modules.linux.users.name    target
    Should Be Equal    ${output}    sysbot

group method works
    ${output}=    Call Components    modules.linux.users.group    target
    Should Be Equal    ${output}[0]    sysbot

uid method works
    ${output}=    Call Components    modules.linux.users.uid    target    sysbot
    Should Be Equal    ${output}    1001

gid method works
    ${output}=    Call Components    modules.linux.users.gid    target    sysbot
    Should Be Equal    ${output}    1001

gids method works
    ${output}=    Call Components    modules.linux.users.gids    target    sysbot
    Should Be Equal    ${output}[0]    1001

groups method works
    ${output}=    Call Components    modules.linux.users.groups    target    sysbot
    Should Be Equal    ${output}[0]    sysbot

home method works
    ${output}=    Call Components    modules.linux.users.home    target    sysbot
    Should Be Equal    ${output}    /home/sysbot

shell method works
    ${output}=    Call Components    modules.linux.users.shell    target    sysbot
    Should Be Equal    ${output}    /bin/bash
