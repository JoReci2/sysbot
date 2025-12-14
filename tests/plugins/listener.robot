*** Settings ***
Name           Database Listener Tests

*** Test Cases ***

Test Case 1 - Simple Pass Test
    [Documentation]    A simple test that should pass
    [Tags]    smoke    database
    Log    This is a passing test
    Should Be Equal    ${1}    ${1}

Test Case 2 - Another Pass Test
    [Documentation]    Another simple test that should pass
    [Tags]    database
    ${result}=    Evaluate    2 + 2
    Should Be Equal As Integers    ${result}    4

Test Case 3 - String Comparison Test
    [Documentation]    Test with string comparison
    [Tags]    database
    ${text}=    Set Variable    Hello World
    Should Contain    ${text}    World
