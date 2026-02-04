*** Settings ***
Name           data

Library        Collections
Library        sysbot.Sysbot

*** Test Cases ***

Load CSV files and retrieve the values ​​as an object without secret    
    ${vars}=    Call Components    plugins.data.csv    tests/.dataset/test.csv
    Should Be Equal As Integers    ${vars}[0][id]    1
    Should Be Equal    ${vars}[0][name]    Alice

Load YAML files and retrieve the values ​​as an object without secret
    ${vars}=    Call Components    plugins.data.yaml    tests/.dataset/test.yml
    Should Be Equal As Integers    ${vars}[dataset][0][id]    1
    Should Be Equal    ${vars}[dataset][0][name]    Sample Item 1

Load JSON files and retrieve the values ​​as an object without secret
    ${vars}=    Call Components    plugins.data.json    tests/.dataset/test.json
    Should Be Equal As Integers    ${vars}[dataset][0][id]    1
    Should Be Equal    ${vars}[dataset][0][name]    Sample Item 1

Load CSV files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.csv    tests/.dataset/test.csv    key=csv

    ${secret}=    Get Secret    csv.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    csv.0.name
    Should Be Equal    ${secret}    Alice

Load YAML files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.yaml    tests/.dataset/test.yml    key=yaml

    ${secret}=    Get Secret    yaml.dataset.0.id
    Should Be Equal As Integers    ${secret}    1

    ${secret}=    Get Secret    yaml.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1

Load JSON files and retrieve the values ​​as an object with secret
    Call Components    plugins.data.json    tests/.dataset/test.json    key=json

    ${secret}=    Get Secret    json.dataset.0.id
    Should Be Equal As Integers    ${secret}    1
    
    ${secret}=    Get Secret    json.dataset.0.name
    Should Be Equal    ${secret}    Sample Item 1

Load Ansible INI inventory without secret
    ${inventory}=    Call Components    plugins.data.ansible    tests/.dataset/ansible_inventory.ini
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_user]    admin
    Should Be Equal As Integers    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_port]    22
    Should Be Equal    ${inventory}[groups][databases][hosts][db1.example.com][ansible_host]    192.168.2.10

Load Ansible YAML inventory without secret
    ${inventory}=    Call Components    plugins.data.ansible    tests/.dataset/ansible_inventory.yml
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_user]    admin
    Should Be Equal As Integers    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_port]    22
    Should Be Equal    ${inventory}[groups][databases][hosts][db1.example.com][ansible_host]    192.168.2.10

Load Ansible INI inventory with secret
    Call Components    plugins.data.ansible    tests/.dataset/ansible_inventory.ini    key=ansible_ini

    ${webservers}=    Get Secret    ansible_ini.groups.webservers
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_user]    admin

Load Ansible YAML inventory with secret
    Call Components    plugins.data.ansible    tests/.dataset/ansible_inventory.yml    key=ansible_yaml

    ${webservers}=    Get Secret    ansible_yaml.groups.webservers
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_user]    admin

