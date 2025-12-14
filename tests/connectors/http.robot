*** Settings ***
Library        Collections
Library        sysbot.Sysbot

*** Variables ***
${API_HOST}=        httpbin.org
${API_PORT}=        443
${API_USER}=        testuser
${API_PASSWORD}=    testpass
${API_KEY}=         test-api-key-12345

*** Test Cases ***

Test HTTP Generic Connector - No Auth
    [Documentation]    Test HTTP connector without authentication
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

Test HTTP Connector - Basic Auth
    [Documentation]    Test HTTP connector with basic authentication
<<<<<<< HEAD
    Open Session    api    http    basic    ${API_HOST}    ${API_PORT}    ${API_USER}    ${API_PASSWORD}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    ${API_USER}    ${API_PASSWORD}    protocol=https    auth_method=basic
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /basic-auth/${API_USER}/${API_PASSWORD}    options={"method": "GET"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - Bearer Token
    [Documentation]    Test HTTP connector with bearer token authentication
    ${token}=    Set Variable    test-bearer-token-12345
<<<<<<< HEAD
    Open Session    api    http    bearer    ${API_HOST}    ${API_PORT}    protocol=https        token=${token}
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=bearer    token=${token}
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /bearer    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

Test HTTP Connector - API Key in Header
    [Documentation]    Test HTTP connector with API key in header
<<<<<<< HEAD
    Open Session    api    http    apikey    ${API_HOST}    ${API_PORT}    protocol=https        login=${API_KEY}    api_key_name=X-API-Key    api_key_location=header
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=apikey    login=${API_KEY}    api_key_name=X-API-Key    api_key_location=header
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /headers    options={"method": "GET"}
    Should Contain    ${response.text}    X-Api-Key
    Close Session    api

Test HTTP Connector - API Key in Query
    [Documentation]    Test HTTP connector with API key in query parameter
<<<<<<< HEAD
    Open Session    api    http    apikey    ${API_HOST}    ${API_PORT}    protocol=https        login=${API_KEY}    api_key_name=api_key    api_key_location=query
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=apikey    login=${API_KEY}    api_key_name=api_key    api_key_location=query
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Contain    ${response.text}    api_key
    Close Session    api

Test HTTP Connector - POST with JSON
    [Documentation]    Test HTTP connector with POST request and JSON body
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${json_data}=    Create Dictionary    name=test    value=123
    ${response}=    Execute Command    api    /post    options={"method": "POST", "json": ${json_data}}
    Should Be Equal As Numbers    ${response.status_code}    200
    Should Contain    ${response.text}    test
    Close Session    api

Test HTTP Connector - PUT with Data
    [Documentation]    Test HTTP connector with PUT request
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /put    options={"method": "PUT", "data": "test data"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - DELETE
    [Documentation]    Test HTTP connector with DELETE request
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /delete    options={"method": "DELETE"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - Custom Headers
    [Documentation]    Test HTTP connector with custom headers
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
=======
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${headers}=    Create Dictionary    X-Custom-Header=CustomValue
    ${response}=    Execute Command    api    /headers    options={"method": "GET", "headers": ${headers}}
    Should Contain    ${response.text}    X-Custom-Header
    Close Session    api

Test HTTP Connector - HTTP Protocol
    [Documentation]    Test HTTP connector with HTTP (not HTTPS)
<<<<<<< HEAD
    Open Session    api    http    http    ${API_HOST}    80    protocol=http    
=======
    Open Session    api    http    http    ${API_HOST}    80    protocol=http    auth_method=none
>>>>>>> e8aec21 (Refactor: move HTTP connector to single file sysbot/connectors/http.py with Http class)
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

