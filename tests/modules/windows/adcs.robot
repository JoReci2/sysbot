*** Settings ***
Name           windows.adcs

Library        Collections
Library        sysbot.Sysbot

Suite Teardown    Close All Sessions
Suite Setup       Init test suite

*** Variables ***
${PORT}=        5986

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    target    winrm    powershell    connexion.host    ${PORT}    connexion.username    connexion.password    is_secret=True

*** Test Cases ***
get_ca method works
    ${output}=    Call Components    modules.windows.adcs.get_ca    target
    Should Be True    isinstance($output, dict)

get_ca_property method works
    ${output}=    Call Components    modules.windows.adcs.get_ca_property    target
    Should Be True    isinstance($output, dict)

get_issued_certificates method works
    ${output}=    Call Components    modules.windows.adcs.get_issued_certificates    target
    Should Be True    isinstance($output, list)

get_pending_requests method works
    ${output}=    Call Components    modules.windows.adcs.get_pending_requests    target
    Should Be True    isinstance($output, list)

get_failed_requests method works
    ${output}=    Call Components    modules.windows.adcs.get_failed_requests    target
    Should Be True    isinstance($output, list)

get_certificate_templates method works
    ${output}=    Call Components    modules.windows.adcs.get_certificate_templates    target
    Should Be True    isinstance($output, list)

get_crl method works
    ${output}=    Call Components    modules.windows.adcs.get_crl    target
    Should Be True    isinstance($output, dict)

get_revoked_certificates method works
    ${output}=    Call Components    modules.windows.adcs.get_revoked_certificates    target
    Should Be True    isinstance($output, list)
