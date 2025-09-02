*** Settings ***
Name           linux.file

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***
is_present method works
    ${output}=    Call Components    modules.linux.file.is_present    target    /etc/hosts
    Should Be True    ${output}

is_file method works
    ${output}=    Call Components    modules.linux.file.is_file    target    /etc/hosts
    Should Be True    ${output}

is_directory method works
    ${output}=    Call Components    modules.linux.file.is_directory    target    /etc
    Should Be True    ${output}

is_executable method works
    ${output}=    Call Components    modules.linux.file.is_executable    target    /etc
    Should Be True    ${output}

is_pipe method works
    ${output}=    Call Components    modules.linux.file.is_pipe    target    /etc
    Should Not Be True    ${output}

is_socket method works
    ${output}=    Call Components    modules.linux.file.is_socket    target    /run/docker.sock
    Should Be True    ${output}

is_symlink method works
    ${output}=    Call Components    modules.linux.file.is_symlink    target    /etc/systemd/system/systemd-homed.service.wants/systemd-homed-activate.service
    Should Be True    ${output}

realpath method works
    ${output}=    Call Components    modules.linux.file.realpath    target    /etc/systemd/system/systemd-homed.service.wants/systemd-homed-activate.service
    Should Be Equal    ${output}    /usr/lib/systemd/system/systemd-homed-activate.service

user method works
    ${output}=    Call Components    modules.linux.file.user    target    /etc/hosts
    Should Be Equal    ${output}    root

uid method works
    ${output}=    Call Components    modules.linux.file.uid    target    /etc/hosts
    Should Be Equal    ${output}    0

group method works
    ${output}=    Call Components    modules.linux.file.group    target    /etc/hosts
    Should Be Equal    ${output}    root

gid method works
    ${output}=    Call Components    modules.linux.file.gid    target    /etc/hosts
    Should Be Equal    ${output}    0

mode method works
    ${output}=    Call Components    modules.linux.file.mode    target    /etc/hosts
    Should Be Equal    ${output}    644

size method works
    ${output}=    Call Components    modules.linux.file.size    target    /etc/hosts
    Should Be Equal    ${output}    384

md5sum method works
    ${output}=    Call Components    modules.linux.file.md5sum    target    /etc/hosts
    Should Be Equal    ${output}    34237b3f095501aac5a64024e4ad4b7c

content method works
    ${output}=    Call Components    modules.linux.file.content    target    /etc/hostname
    Should Be Equal    ${output}    lab01

contains method works
    ${output}=    Call Components    modules.linux.file.contains    target    /etc/hosts    127.0.0.1
    Should Be True    ${output}