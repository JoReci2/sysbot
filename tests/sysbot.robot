*** Settings ***
Name           Sysbot
Description    Fonctionnal tests for main sysbot

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${HOST}=          192.168.1.112
${PORT}=        22
${USER}=       sysbot
${PASSWORD}=   P@ssw0rd

*** Settings ***
Suite Setup       Call Components    plugins.data.yaml    connexion    tests/.dataset/connexion.yml    is_secret=True
Suite Teardown    Close All Sessions

*** Test Cases ***

Open Session without secret is available
    Open Session    target    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close All Sessions

Open Session with secret is available
    Open Session    target    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True
    Close All Sessions

Open multiple session without conflict
    Open Session    target1    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Open Session    target2    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close All Sessions

Open multiple session with secret and not
    Open Session    target1    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True
    Open Session    target2    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close All Sessions

Open multiple session then close one
    Open Session    target1    ssh    bash    connexion.host    ${PORT}   connexion.username    connexion.password    is_secret=True
    Open Session    target2    ssh    bash    ${HOST}    ${PORT}   ${USER}    ${PASSWORD}
    Close Session    target1

Add/Get/Remove secret fonctionnality is available
    Add Secret    my_secret    very_secret_value
    ${secret}=    Get Secret    my_secret
    Should Be Equal    ${secret}    very_secret_value
    Remove Secret    my_secret
    Run Keyword And Expect Error    KeyError: "Secret 'my_secret' not found"    Get Secret    my_secret
