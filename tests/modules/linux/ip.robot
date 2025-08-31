*** Settings ***
Name           linux.ip

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

addr method works
    ${output}=    Call Components    modules.linux.ip.addr    target    enp1s0
    Should Be Equal As Integers    ${output}[0][mtu]    1500
    Should Be Equal    ${output}[0][addr_info][0][local]    192.168.1.112

route method works
    ${output}=    Call Components    modules.linux.ip.route    target
    Should Be Equal    ${output}[0][gateway]    192.168.1.254

speed method works
    ${output}=    Call Components    modules.linux.ip.speed    target    enp1s0
    Should Be Equal    ${output}    1000

link method works
    ${output}=    Call Components    modules.linux.ip.link    target    enp1s0
    Should Be Equal As Integers    ${output}[0][mtu]    1500

resolve method works
    ${output}=    Call Components    modules.linux.ip.resolve    target    www.google.com
    Should Contain    ${output}    2a00:1450:4007

ping method works
    ${output}=    Call Components    modules.linux.ip.ping    target    www.google.com
    Should Be Equal    ${output}    0
