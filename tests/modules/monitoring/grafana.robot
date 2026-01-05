*** Settings ***
Name           monitoring.grafana

Library        Collections
Library        sysbot.Sysbot

Suite Setup       Init test suite
Suite Teardown    Close All Sessions

*** Variables ***
${PORT}=        3000

*** Keywords ***

Init test suite
    Call Components    plugins.data.yaml    tests/.dataset/connexion.yml    key=connexion
    Open Session    grafana    http    apikey    connexion.host    ${PORT}    api_key=connexion.api_key    is_secret=True

Test Get Datasource By Id
    [Arguments]    ${datasources}
    ${datasource}=    Get From List    ${datasources}    0
    ${datasource_id}=    Get From Dictionary    ${datasource}    id
    ${output}=    Call Components    modules.monitoring.grafana.get_datasource_by_id    grafana    ${datasource_id}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    id
    Dictionary Should Contain Key    ${output}    name

Test Get Datasource By Name
    [Arguments]    ${datasources}
    ${datasource}=    Get From List    ${datasources}    0
    ${datasource_name}=    Get From Dictionary    ${datasource}    name
    ${output}=    Call Components    modules.monitoring.grafana.get_datasource_by_name    grafana    ${datasource_name}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    id
    Dictionary Should Contain Key    ${output}    name

Test Get Dashboard By Uid
    [Arguments]    ${dashboards}
    ${dashboard}=    Get From List    ${dashboards}    0
    ${dashboard_uid}=    Get From Dictionary    ${dashboard}    uid
    ${output}=    Call Components    modules.monitoring.grafana.get_dashboard_by_uid    grafana    ${dashboard_uid}
    Should Not Be Empty    ${output}
    Dictionary Should Contain Key    ${output}    dashboard

*** Test Cases ***

health_check method works
    ${output}=    Call Components    modules.monitoring.grafana.health_check    grafana
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    dict

get_datasources method works
    ${output}=    Call Components    modules.monitoring.grafana.get_datasources    grafana
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

search_dashboards method works
    ${output}=    Call Components    modules.monitoring.grafana.search_dashboards    grafana
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

get_home_dashboard method works
    ${output}=    Call Components    modules.monitoring.grafana.get_home_dashboard    grafana
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    dict

get_current_user method works
    ${output}=    Call Components    modules.monitoring.grafana.get_current_user    grafana
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    dict
    Dictionary Should Contain Key    ${output}    id

get_current_organization method works
    ${output}=    Call Components    modules.monitoring.grafana.get_current_organization    grafana
    Should Not Be Empty    ${output}
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    dict
    Dictionary Should Contain Key    ${output}    id

get_folders method works
    ${output}=    Call Components    modules.monitoring.grafana.get_folders    grafana
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

get_alerts method works
    ${output}=    Call Components    modules.monitoring.grafana.get_alerts    grafana
    ${type}=    Evaluate    type($output).__name__
    Should Be Equal    ${type}    list

get_datasource_by_id method works with existing datasource
    ${datasources}=    Call Components    modules.monitoring.grafana.get_datasources    grafana
    ${length}=    Get Length    ${datasources}
    Run Keyword If    ${length} > 0    Test Get Datasource By Id    ${datasources}

get_datasource_by_name method works with existing datasource
    ${datasources}=    Call Components    modules.monitoring.grafana.get_datasources    grafana
    ${length}=    Get Length    ${datasources}
    Run Keyword If    ${length} > 0    Test Get Datasource By Name    ${datasources}

get_dashboard_by_uid method works with existing dashboard
    ${dashboards}=    Call Components    modules.monitoring.grafana.search_dashboards    grafana
    ${length}=    Get Length    ${dashboards}
    Run Keyword If    ${length} > 0    Test Get Dashboard By Uid    ${dashboards}
