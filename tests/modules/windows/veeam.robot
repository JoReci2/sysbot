*** Settings ***
Name           windows.veeam

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
    ${output}=    Call Components    modules.windows.veeam.get_server    target
    Should Be True    isinstance($output, list)

get_backup_repository method works
    ${output}=    Call Components    modules.windows.veeam.get_backup_repository    target
    Should Be True    isinstance($output, list)

get_job method works
    ${output}=    Call Components    modules.windows.veeam.get_job    target
    Should Be True    isinstance($output, list)

get_backup method works
    ${output}=    Call Components    modules.windows.veeam.get_backup    target
    Should Be True    isinstance($output, list)

get_restore_point method works
    ${output}=    Call Components    modules.windows.veeam.get_restore_point    target
    Should Be True    isinstance($output, list)

get_backup_session method works
    ${output}=    Call Components    modules.windows.veeam.get_backup_session    target
    Should Be True    isinstance($output, list)

get_vi_server method works
    ${output}=    Call Components    modules.windows.veeam.get_vi_server    target
    Should Be True    isinstance($output, list)

get_server_session method works
    ${output}=    Call Components    modules.windows.veeam.get_server_session    target
    Should Be True    isinstance($output, list)
