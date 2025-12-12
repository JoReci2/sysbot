*** Settings ***
Name           windows.file

Library        Collections
Library        sysbot.Sysbot

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Test Cases ***
is_present method works
    ${output}=    Call Components    modules.windows.file.is_present    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Be True    ${output}

is_file method works
    ${output}=    Call Components    modules.windows.file.is_file    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Be True    ${output}

is_directory method works
    ${output}=    Call Components    modules.windows.file.is_directory    target    C:\\Windows
    Should Be True    ${output}

is_directory on file returns false
    ${output}=    Call Components    modules.windows.file.is_directory    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Not Be True    ${output}

is_file on directory returns false
    ${output}=    Call Components    modules.windows.file.is_file    target    C:\\Windows
    Should Not Be True    ${output}

size method works
    ${output}=    Call Components    modules.windows.file.size    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Not Be Empty    ${output}
    Should Match Regexp    ${output}    ^\\d+$

content method works
    ${output}=    Call Components    modules.windows.file.content    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Not Be Empty    ${output}

md5 method works
    ${output}=    Call Components    modules.windows.file.md5    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Should Not Be Empty    ${output}
    Should Match Regexp    ${output}    ^[A-F0-9]{32}$

attributes method works
    ${output}=    Call Components    modules.windows.file.attributes    target    C:\\Windows\\System32\\drivers\\etc\\hosts
    Dictionary Should Contain Key    ${output}    Name
    Dictionary Should Contain Key    ${output}    FullName
    Dictionary Should Contain Key    ${output}    Length

contains method works
    ${output}=    Call Components    modules.windows.file.contains    target    C:\\Windows\\System32\\drivers\\etc\\hosts    localhost
    Should Be True    ${output}

contains method returns false for non-existing pattern
    ${output}=    Call Components    modules.windows.file.contains    target    C:\\Windows\\System32\\drivers\\etc\\hosts    nonexistentpattern123456789
    Should Not Be True    ${output}

owner method works
    ${output}=    Call Components    modules.windows.file.owner    target    C:\\Windows
    Should Not Be Empty    ${output}

permissions method works
    ${output}=    Call Components    modules.windows.file.permissions    target    C:\\Windows
    Dictionary Should Contain Key    ${output}    Owner
    Dictionary Should Contain Key    ${output}    Access

list_directory method works
    ${output}=    Call Components    modules.windows.file.list_directory    target    C:\\Windows\\System32\\drivers\\etc
    Should Not Be Empty    ${output}
