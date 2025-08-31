*** Settings ***
Name           data

Library        Collections
Library        sysbot.Sysbot

*** Test Cases ***

Load CSV files and retrieve the values ​​as an object without secret    
    ${vars}=    Call Components    plugins.data.csv    csv    tests/.dataset/test.csv
    Should Be Equal As Integers    ${vars}[0][id]    1
    Should Be Equal    ${vars}[0][name]    Alice

Load YAML files and retrieve the values ​​as an object without secret
    ${vars}=    Call Components    plugins.data.yaml    yaml    tests/.dataset/test.yml
    Should Be Equal As Integers    ${vars}[dataset][0][id]    1
    Should Be Equal    ${vars}[dataset][0][name]    Sample Item 1

Load JSON files and retrieve the values ​​as an object without secret
    ${vars}=    Call Components    plugins.data.json    json    tests/.dataset/test.json
    Should Be Equal As Integers    ${vars}[dataset][0][id]    1
    Should Be Equal    ${vars}[dataset][0][name]    Sample Item 1

Load CSV files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.csv    csv    tests/.dataset/test.csv    is_secret=True

    ${secret}=    Get Secret    csv.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    csv.0.name
    Should Be Equal    ${secret}    Alice

Load YAML files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.yaml    yaml    tests/.dataset/test.yml    is_secret=True

    ${secret}=    Get Secret    yaml.dataset.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    yaml.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1

Load JSON files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.json    json    tests/.dataset/test.json    is_secret=True

    ${secret}=    Get Secret    json.dataset.0.id
    Should Be Equal As Integers    ${secret}    1
    
    ${secret}=    Get Secret    json.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1

