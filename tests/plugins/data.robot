*** Settings ***
Name           Fonctionnal tests linux for data plugins

Library        Collections
Library        sysbot.Sysbot

*** Test Cases ***

It is possible to load CSV files and retrieve the values ​​as an object
    Call Components    plugins.data.csv    csv    tests/plugins/dataset/test.csv

    ${secret}=    Get Secret    csv.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    csv.0.name
    Should Be Equal    ${secret}    Alice

It is possible to load YAML files and retrieve the values ​​as an object
    Call Components    plugins.data.yaml    yaml    tests/plugins/dataset/test.yml
    
    ${secret}=    Get Secret    yaml.dataset.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    yaml.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1

It is possible to load JSON files and retrieve the values ​​as an object
    Call Components    plugins.data.json    json    tests/plugins/dataset/test.json

    ${secret}=    Get Secret    json.dataset.0.id
    Should Be Equal As Integers    ${secret}    1
    
    ${secret}=    Get Secret    json.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1