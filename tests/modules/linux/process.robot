*** Settings ***
Name           linux.process

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

ps method works
    ${output}=    Call Components    modules.linux.process.ps    target    bash
    Should Contain    ${output}[0][command]    bash

thread method works
    ${output}=    Call Components    modules.linux.process.thread    target    bash
    Should Contain    ${output}[0][tty]    bash

security method works
    ${output}=    Call Components    modules.linux.process.security    target    bash
    Should Contain    ${output}[0][comm]    bash
