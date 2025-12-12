*** Settings ***
Name           windows.adds

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
get_domain method works
    ${output}=    Call Components    modules.windows.adds.get_domain    target
    Should Be True    isinstance($output, dict)
    Dictionary Should Contain Key    ${output}    DNSRoot

get_forest method works
    ${output}=    Call Components    modules.windows.adds.get_forest    target
    Should Be True    isinstance($output, dict)
    Dictionary Should Contain Key    ${output}    Name

get_domain_controller method works
    ${output}=    Call Components    modules.windows.adds.get_domain_controller    target
    Should Be True    isinstance($output, dict)
    Dictionary Should Contain Key    ${output}    HostName

get_users method works
    ${output}=    Call Components    modules.windows.adds.get_users    target
    Should Be True    isinstance($output, list)

get_groups method works
    ${output}=    Call Components    modules.windows.adds.get_groups    target
    Should Be True    isinstance($output, list)

get_organizational_units method works
    ${output}=    Call Components    modules.windows.adds.get_organizational_units    target
    Should Be True    isinstance($output, list)

get_computers method works
    ${output}=    Call Components    modules.windows.adds.get_computers    target
    Should Be True    isinstance($output, list)

get_gpo method works
    ${output}=    Call Components    modules.windows.adds.get_gpo    target
    Should Be True    isinstance($output, list)

get_gpos method works
    ${output}=    Call Components    modules.windows.adds.get_gpos    target
    Should Be True    isinstance($output, list)
