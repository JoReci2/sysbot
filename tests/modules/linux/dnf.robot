*** Settings ***
Name           Fonctionnal tests linux for dnf module

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${PORT}=        22

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    connexion    tests/.dataset/connexion.yml
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password

*** Settings ***

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Test Cases ***

repolist method works
    ${output}=    Call Components    modules.linux.dnf.repolist    target
    Should Not Be Empty    ${output}[0][name]

repofile method works
    ${output}=    Call Components    modules.linux.dnf.repofile    target    /etc/yum.repos.d/fedora.repo
    Should Be Equal    ${output}[fedora][enabled]    1
