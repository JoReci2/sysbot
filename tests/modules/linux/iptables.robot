*** Settings ***
Name           linux.iptables

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

list_rules method works
    ${output}=    Call Components    modules.linux.iptables.list_rules    target    filter    runas=True
    Should Contain Any    ${output}    Chain INPUT    Chain OUTPUT    Chain FORWARD

list_rules_line_numbers method works
    ${output}=    Call Components    modules.linux.iptables.list_rules_line_numbers    target    filter    INPUT    runas=True
    Should Contain    ${output}    Chain INPUT

get_policy method works
    ${output}=    Call Components    modules.linux.iptables.get_policy    target    INPUT    filter    runas=True
    Should Match Regexp    ${output}    ^(ACCEPT|DROP|REJECT)$

list_chains method works
    ${output}=    Call Components    modules.linux.iptables.list_chains    target    filter    runas=True
    Should Contain    ${output}    INPUT
    Should Contain    ${output}    OUTPUT
    Should Contain    ${output}    FORWARD

count_rules method works
    ${output}=    Call Components    modules.linux.iptables.count_rules    target    INPUT    filter    runas=True
    Should Be True    ${output} >= 0

save_rules method works
    ${output}=    Call Components    modules.linux.iptables.save_rules    target    runas=True
    Should Contain    ${output}    *filter

list_by_spec method works
    ${output}=    Call Components    modules.linux.iptables.list_by_spec    target    filter    INPUT    runas=True
    Should Contain    ${output}    -P INPUT
