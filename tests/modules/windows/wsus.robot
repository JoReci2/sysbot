*** Settings ***
Name           windows.wsus

Library        Collections
Library        sysbot.Sysbot

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}    connexion.username    connexion.password    is_secret=True

*** Test Cases ***
get_server method works
    ${output}=    Call Components    modules.windows.wsus.get_server    target
    Should Be True    isinstance($output, dict)
    Dictionary Should Contain Key    ${output}    Name

get_update method works
    ${output}=    Call Components    modules.windows.wsus.get_update    target
    Should Be True    isinstance($output, list)

get_computer method works
    ${output}=    Call Components    modules.windows.wsus.get_computer    target
    Should Be True    isinstance($output, list)

get_classification method works
    ${output}=    Call Components    modules.windows.wsus.get_classification    target
    Should Be True    isinstance($output, list)

get_product method works
    ${output}=    Call Components    modules.windows.wsus.get_product    target
    Should Be True    isinstance($output, list)

get_status method works
    ${output}=    Call Components    modules.windows.wsus.get_status    target
    Should Be True    isinstance($output, dict)
