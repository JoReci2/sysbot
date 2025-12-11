*** Settings ***
Name           windows.firewall

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Test Cases ***
getProfiles method works
    ${output}=    Call Components    modules.windows.firewall.getProfiles    target
    Should Not Be Empty    ${output}
    ${first_profile}=    Set Variable    ${output}[0]
    Should Contain Any    ${first_profile}[Name]    Domain    Private    Public

getProfile method works
    ${output}=    Call Components    modules.windows.firewall.getProfile    target    Public
    Should Be Equal    ${output}[Name]    Public
    Dictionary Should Contain Key    ${output}    Enabled
    Dictionary Should Contain Key    ${output}    DefaultInboundAction

getRules method works
    ${output}=    Call Components    modules.windows.firewall.getRules    target
    Should Not Be Empty    ${output}
    ${first_rule}=    Set Variable    ${output}[0]
    Dictionary Should Contain Key    ${first_rule}    Name
    Dictionary Should Contain Key    ${first_rule}    DisplayName
    Dictionary Should Contain Key    ${first_rule}    Enabled

getEnabledRules method works
    ${output}=    Call Components    modules.windows.firewall.getEnabledRules    target
    Should Not Be Empty    ${output}
    ${first_rule}=    Set Variable    ${output}[0]
    Should Be Equal    ${first_rule}[Enabled]    True

getInboundRules method works
    ${output}=    Call Components    modules.windows.firewall.getInboundRules    target
    Should Not Be Empty    ${output}
    ${first_rule}=    Set Variable    ${output}[0]
    Should Be Equal    ${first_rule}[Direction]    Inbound

getOutboundRules method works
    ${output}=    Call Components    modules.windows.firewall.getOutboundRules    target
    Should Not Be Empty    ${output}
    ${first_rule}=    Set Variable    ${output}[0]
    Should Be Equal    ${first_rule}[Direction]    Outbound

getPortFilters method works
    ${output}=    Call Components    modules.windows.firewall.getPortFilters    target
    Should Not Be Empty    ${output}

getAddressFilters method works
    ${output}=    Call Components    modules.windows.firewall.getAddressFilters    target
    Should Not Be Empty    ${output}
