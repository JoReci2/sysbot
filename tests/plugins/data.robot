*** Settings ***
Name           Fonctionnal tests linux for data plugins

Library        Collections
Library        sysbot.Sysbot

*** Test Cases ***

It is possible to load CSV files and retrieve the values ​​as an object
    ${output}=    Call Components    plugins.data.csv    tests/plugins/dataset/test.csv
    Should Be Equal    ${output}[0][name]    thibault
    Should Be Equal As Integers    ${output}[0][age]    25
    Should Be Equal    ${output}[1][name]    shannon
    Should Be Equal As Integers    ${output}[1][age]    30

It is possible to load YAML files and retrieve the values ​​as an object
    ${output}=    Call Components    plugins.data.yaml    tests/plugins/dataset/test.yml
    Should Be Equal As Integers    ${output}[dataset][0][id]    1
    Should Be Equal    ${output}[dataset][0][name]    Sample Item 1