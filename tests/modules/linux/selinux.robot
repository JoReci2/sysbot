*** Settings ***
Name           linux.selinux

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
sestatus method works
    ${result}=    Call Components    modules.linux.selinux.sestatus    target
    Should Be Equal    ${result}[selinux_status]    enabled

getenforce method works
    ${result}=    Call Components    modules.linux.selinux.getenforce    target
    Should Be Equal    ${result}    Enforcing

context_id method works
    ${result}=    Call Components    modules.linux.selinux.context_id    target
    Should Contain    ${result}      unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023

context_ps method works
    ${result}=    Call Components    modules.linux.selinux.context_ps    target    bash
    Should Contain    ${result}      unconfined_u:unconfined_r:unconfined_t

context_file method works
    ${result}=    Call Components    modules.linux.selinux.context_file    target    .bashrc
    Should Contain    ${result}    unconfined_u:object_r:user_home_t

getsebool method works
    ${result}=    Call Components    modules.linux.selinux.getsebool    target
    Should Be Equal    ${result}[abrt_anon_write]    off
