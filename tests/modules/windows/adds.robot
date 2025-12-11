*** Settings ***
Name           windows.adds

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***
get_domain method works
    ${output}=    Call Components    modules.windows.adds.get_domain    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Name
    Dictionary Should Contain Key    ${output}    DNSRoot

get_forest method works
    ${output}=    Call Components    modules.windows.adds.get_forest    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Name
    Dictionary Should Contain Key    ${output}    RootDomain

get_domain_controller method works
    ${output}=    Call Components    modules.windows.adds.get_domain_controller    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Name
    Dictionary Should Contain Key    ${output}    Domain

get_users method works
    ${output}=    Call Components    modules.windows.adds.get_users    target
    Should Not Be Empty    ${output}
    ${first_user}=    Get From List    ${output}    0
    Dictionary Should Contain Key    ${first_user}    SamAccountName
    Dictionary Should Contain Key    ${first_user}    Name

get_groups method works
    ${output}=    Call Components    modules.windows.adds.get_groups    target
    Should Not Be Empty    ${output}
    ${first_group}=    Get From List    ${output}    0
    Dictionary Should Contain Key    ${first_group}    SamAccountName
    Dictionary Should Contain Key    ${first_group}    Name

get_organizational_units method works
    ${output}=    Call Components    modules.windows.adds.get_organizational_units    target
    Should Not Be Empty    ${output}
    ${first_ou}=    Get From List    ${output}    0
    Dictionary Should Contain Key    ${first_ou}    Name
    Dictionary Should Contain Key    ${first_ou}    DistinguishedName

get_computers method works
    ${output}=    Call Components    modules.windows.adds.get_computers    target
    Should Not Be Empty    ${output}
    ${first_computer}=    Get From List    ${output}    0
    Dictionary Should Contain Key    ${first_computer}    Name
    Dictionary Should Contain Key    ${first_computer}    DNSHostName
