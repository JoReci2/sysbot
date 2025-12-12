*** Settings ***
Name           windows.dnsserver

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
    ${output}=    Call Components    modules.windows.dnsserver.get_server    target
    Should Be True    isinstance($output, dict)
    Dictionary Should Contain Key    ${output}    ServerSetting

get_zones method works
    ${output}=    Call Components    modules.windows.dnsserver.get_zones    target
    Should Be True    isinstance($output, list)

get_forwarder method works
    ${output}=    Call Components    modules.windows.dnsserver.get_forwarder    target
    Should Be True    isinstance($output, dict)

get_cache method works
    ${output}=    Call Components    modules.windows.dnsserver.get_cache    target
    Should Be True    isinstance($output, dict)

get_statistics method works
    ${output}=    Call Components    modules.windows.dnsserver.get_statistics    target
    Should Be True    isinstance($output, dict)

get_setting method works
    ${output}=    Call Components    modules.windows.dnsserver.get_setting    target
    Should Be True    isinstance($output, dict)
