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

Execute Ansible playbook without parameters
    ${result}=    Call Components    plugins.ansible.playbook    tests/.dataset/test_playbook.yml
    Should Be Equal    ${result}[success]    ${True}
    Should Be Equal As Integers    ${result}[rc]    0
    Should Contain    ${result}[stdout]    Hello from Ansible playbook

Execute Ansible playbook with extra variables
    ${extra_vars}=    Create Dictionary    version=1.2.3
    ${result}=    Call Components    plugins.ansible.playbook    tests/.dataset/test_playbook.yml    extra_vars=${extra_vars}
    Should Be Equal    ${result}[success]    ${True}
    Should Contain    ${result}[stdout]    Version: 1.2.3

Execute Ansible playbook in check mode
    ${result}=    Call Components    plugins.ansible.playbook    tests/.dataset/test_playbook.yml    check=${True}
    Should Be Equal    ${result}[success]    ${True}
    Should Be Equal As Integers    ${result}[rc]    0

Execute Ansible playbook with verbose output
    ${result}=    Call Components    plugins.ansible.playbook    tests/.dataset/test_playbook.yml    verbose=${1}
    Should Be Equal    ${result}[success]    ${True}
    Should Contain    ${result}[stdout]    TASK

Execute Ansible playbook and check stats
    ${result}=    Call Components    plugins.ansible.playbook    tests/.dataset/test_playbook.yml
    Should Be Equal    ${result}[success]    ${True}
    Dictionary Should Contain Key    ${result}    stats
    Should Not Be Empty    ${result}[stats]

Execute Ansible role on localhost
    ${result}=    Call Components    plugins.ansible.role    test_role    hosts=localhost    roles_path=tests/.dataset/roles
    Should Be Equal    ${result}[success]    ${True}
    Should Be Equal As Integers    ${result}[rc]    0
    Should Contain    ${result}[stdout]    Test role is being executed

Execute Ansible role with extra variables
    ${extra_vars}=    Create Dictionary    custom_var=test_value_123
    ${result}=    Call Components    plugins.ansible.role    test_role    hosts=localhost    roles_path=tests/.dataset/roles    extra_vars=${extra_vars}
    Should Be Equal    ${result}[success]    ${True}
    Should Contain    ${result}[stdout]    Custom variable: test_value_123

Execute Ansible role in check mode
    ${result}=    Call Components    plugins.ansible.role    test_role    hosts=localhost    roles_path=tests/.dataset/roles    check=${True}
    Should Be Equal    ${result}[success]    ${True}
    Should Be Equal As Integers    ${result}[rc]    0

Execute Ansible role with verbose output
    ${result}=    Call Components    plugins.ansible.role    test_role    hosts=localhost    roles_path=tests/.dataset/roles    verbose=${1}
    Should Be Equal    ${result}[success]    ${True}
    Should Contain    ${result}[stdout]    TASK

Execute Ansible role with inventory
    ${result}=    Call Components    plugins.ansible.role    test_role    hosts=webservers    inventory=tests/.dataset/ansible_inventory.ini    roles_path=tests/.dataset/roles
    Should Be Equal    ${result}[success]    ${True}
    Should Be Equal As Integers    ${result}[rc]    0
