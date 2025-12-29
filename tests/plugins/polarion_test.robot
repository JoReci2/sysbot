*** Settings ***
Documentation    Test cases for Polarion plugin integration
...              This suite demonstrates how to use Polarion tags for test case mapping

*** Test Cases ***

Test Case With Polarion ID
    [Documentation]    This test is linked to a Polarion test case
    [Tags]    polarion-id:TEST-001    polarion-title:Basic Test Case    smoke
    Log    Test linked to Polarion TEST-001
    Should Be Equal    ${1}    ${1}

Test Case With Custom Properties
    [Documentation]    This test includes custom Polarion properties
    [Tags]    polarion-id:TEST-002    polarion-testEnvironment:Production    polarion-assignee:jdoe
    Log    Test with custom properties
    ${result}=    Evaluate    2 + 2
    Should Be Equal As Integers    ${result}    4

Test Case Without Polarion Tags
    [Documentation]    This test has no Polarion mapping
    [Tags]    regression
    Log    Test without Polarion tags
    Should Contain    Hello World    World

Test Case With Failure
    [Documentation]    This test should fail
    [Tags]    polarion-id:TEST-003    polarion-priority:High
    Log    This test demonstrates a failure
    Should Be Equal    ${1}    ${2}    This is expected to fail
