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

get_domain_controller method works
    ${output}=    Call Components    modules.windows.adds.get_domain_controller    target
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    Name
    Dictionary Should Contain Key    ${output}    Domain

get_users method works
    ${output}=    Call Components    modules.windows.adds.get_users    target
    Should Be True    isinstance($output, list)
    Run Keyword If    len($output) > 0    Dictionary Should Contain Key    ${output}[0]    SamAccountName

get_groups method works
    ${output}=    Call Components    modules.windows.adds.get_groups    target
    Should Be True    isinstance($output, list)
    Run Keyword If    len($output) > 0    Dictionary Should Contain Key    ${output}[0]    SamAccountName

get_ous method works
    ${output}=    Call Components    modules.windows.adds.get_ous    target
    Should Be True    isinstance($output, list)
    Run Keyword If    len($output) > 0    Dictionary Should Contain Key    ${output}[0]    DistinguishedName

get_gpos method works
    ${output}=    Call Components    modules.windows.adds.get_gpos    target
    Should Be True    isinstance($output, list)
    Run Keyword If    len($output) > 0    Dictionary Should Contain Key    ${output}[0]    DisplayName

search_users method works with filter
    ${output}=    Call Components    modules.windows.adds.search_users    target    Name -like '*Admin*'
    Should Be True    isinstance($output, list)

get_user method works with specific user
    [Documentation]    This test requires an existing user - may fail if no users exist
    ${users}=    Call Components    modules.windows.adds.get_users    target
    Run Keyword If    len($users) > 0    Test Get User With First User    ${users}

Test Get User With First User
    [Arguments]    ${users}
    ${first_user_sam}=    Set Variable    ${users}[0][SamAccountName]
    ${output}=    Call Components    modules.windows.adds.get_user    target    ${first_user_sam}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    SamAccountName

get_group method works with specific group
    [Documentation]    This test requires an existing group - may fail if no groups exist
    ${groups}=    Call Components    modules.windows.adds.get_groups    target
    Run Keyword If    len($groups) > 0    Test Get Group With First Group    ${groups}

Test Get Group With First Group
    [Arguments]    ${groups}
    ${first_group_sam}=    Set Variable    ${groups}[0][SamAccountName]
    ${output}=    Call Components    modules.windows.adds.get_group    target    ${first_group_sam}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    SamAccountName

get_group_members method works with specific group
    [Documentation]    This test requires an existing group - may return empty list for groups with no members
    ${groups}=    Call Components    modules.windows.adds.get_groups    target
    Run Keyword If    len($groups) > 0    Test Get Group Members With First Group    ${groups}

Test Get Group Members With First Group
    [Arguments]    ${groups}
    ${first_group_sam}=    Set Variable    ${groups}[0][SamAccountName]
    ${output}=    Call Components    modules.windows.adds.get_group_members    target    ${first_group_sam}
    Should Be True    isinstance($output, list)

get_ou method works with specific ou
    [Documentation]    This test requires an existing OU - may fail if no OUs exist
    ${ous}=    Call Components    modules.windows.adds.get_ous    target
    Run Keyword If    len($ous) > 0    Test Get OU With First OU    ${ous}

Test Get OU With First OU
    [Arguments]    ${ous}
    ${first_ou_dn}=    Set Variable    ${ous}[0][DistinguishedName]
    ${output}=    Call Components    modules.windows.adds.get_ou    target    ${first_ou_dn}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    DistinguishedName

get_gpo method works with specific gpo
    [Documentation]    This test requires an existing GPO - may fail if no GPOs exist
    ${gpos}=    Call Components    modules.windows.adds.get_gpos    target
    Run Keyword If    len($gpos) > 0    Test Get GPO With First GPO    ${gpos}

Test Get GPO With First GPO
    [Arguments]    ${gpos}
    ${first_gpo_name}=    Set Variable    ${gpos}[0][DisplayName]
    ${output}=    Call Components    modules.windows.adds.get_gpo    target    ${first_gpo_name}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    DisplayName

get_gpo_report method works with specific gpo
    [Documentation]    This test requires an existing GPO - may fail if no GPOs exist
    ${gpos}=    Call Components    modules.windows.adds.get_gpos    target
    Run Keyword If    len($gpos) > 0    Test Get GPO Report With First GPO    ${gpos}

Test Get GPO Report With First GPO
    [Arguments]    ${gpos}
    ${first_gpo_name}=    Set Variable    ${gpos}[0][DisplayName]
    ${output}=    Call Components    modules.windows.adds.get_gpo_report    target    ${first_gpo_name}
    Should Not Be Empty    ${output}
    Should Contain    ${output}    <?xml
