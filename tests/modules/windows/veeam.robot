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
get_servers method works
    ${output}=    Call Components    modules.windows.veeam.get_servers    target
    Should Be True    isinstance($output, list)

get_backup_repositories method works
    ${output}=    Call Components    modules.windows.veeam.get_backup_repositories    target
    Should Be True    isinstance($output, list)

get_jobs method works
    ${output}=    Call Components    modules.windows.veeam.get_jobs    target
    Should Be True    isinstance($output, list)

get_backups method works
    ${output}=    Call Components    modules.windows.veeam.get_backups    target
    Should Be True    isinstance($output, list)

get_restore_points method works
    ${output}=    Call Components    modules.windows.veeam.get_restore_points    target
    Should Be True    isinstance($output, list)

get_backup_sessions method works
    ${output}=    Call Components    modules.windows.veeam.get_backup_sessions    target
    Should Be True    isinstance($output, list)

get_vi_servers method works
    ${output}=    Call Components    modules.windows.veeam.get_vi_servers    target
    Should Be True    isinstance($output, list)

get_server_sessions method works
    ${output}=    Call Components    modules.windows.veeam.get_server_sessions    target
    Should Be True    isinstance($output, list)
