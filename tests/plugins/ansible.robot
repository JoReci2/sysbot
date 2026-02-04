*** Settings ***
Name           ansible

Library        Collections
Library        sysbot.Sysbot

*** Test Cases ***

Load Ansible INI inventory without secret
    ${inventory}=    Call Components    plugins.ansible.inventory    tests/.dataset/ansible_inventory.ini
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_user]    admin
    Should Be Equal As Integers    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_port]    22
    Should Be Equal    ${inventory}[groups][databases][hosts][db1.example.com][ansible_host]    192.168.2.10

Load Ansible YAML inventory without secret
    ${inventory}=    Call Components    plugins.ansible.inventory    tests/.dataset/ansible_inventory.yml
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_user]    admin
    Should Be Equal As Integers    ${inventory}[groups][webservers][hosts][web1.example.com][ansible_port]    22
    Should Be Equal    ${inventory}[groups][databases][hosts][db1.example.com][ansible_host]    192.168.2.10

Load Ansible INI inventory with secret
    Call Components    plugins.ansible.inventory    tests/.dataset/ansible_inventory.ini    key=ansible_ini

    ${webservers}=    Get Secret    ansible_ini.groups.webservers
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_user]    admin

Load Ansible YAML inventory with secret
    Call Components    plugins.ansible.inventory    tests/.dataset/ansible_inventory.yml    key=ansible_yaml

    ${webservers}=    Get Secret    ansible_yaml.groups.webservers
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_host]    192.168.1.10
    Should Be Equal    ${webservers}[hosts][web1.example.com][ansible_user]    admin
