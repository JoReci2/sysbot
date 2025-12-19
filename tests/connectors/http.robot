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
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

Test HTTP Connector - Basic Auth
    [Documentation]    Test HTTP connector with basic authentication
    Open Session    api    http    basic    ${API_HOST}    ${API_PORT}    ${API_USER}    ${API_PASSWORD}    protocol=https    
    ${response}=    Execute Command    api    /basic-auth/${API_USER}/${API_PASSWORD}    options={"method": "GET"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - Bearer Token
    [Documentation]    Test HTTP connector with bearer token authentication
    ${token}=    Set Variable    test-bearer-token-12345
    Open Session    api    http    bearer    ${API_HOST}    ${API_PORT}    protocol=https        token=${token}
    ${response}=    Execute Command    api    /bearer    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

Test HTTP Connector - API Key in Header
    [Documentation]    Test HTTP connector with API key in header
    Open Session    api    http    apikey    ${API_HOST}    ${API_PORT}    protocol=https        login=${API_KEY}    api_key_name=X-API-Key    api_key_location=header
    ${response}=    Execute Command    api    /headers    options={"method": "GET"}
    Should Contain    ${response.text}    X-Api-Key
    Close Session    api

Test HTTP Connector - API Key in Query
    [Documentation]    Test HTTP connector with API key in query parameter
    Open Session    api    http    apikey    ${API_HOST}    ${API_PORT}    protocol=https        login=${API_KEY}    api_key_name=api_key    api_key_location=query
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Contain    ${response.text}    api_key
    Close Session    api

Test HTTP Connector - POST with JSON
    [Documentation]    Test HTTP connector with POST request and JSON body
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
    ${json_data}=    Create Dictionary    name=test    value=123
    ${response}=    Execute Command    api    /post    options={"method": "POST", "json": ${json_data}}
    Should Be Equal As Numbers    ${response.status_code}    200
    Should Contain    ${response.text}    test
    Close Session    api

Test HTTP Connector - PUT with Data
    [Documentation]    Test HTTP connector with PUT request
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
    ${response}=    Execute Command    api    /put    options={"method": "PUT", "data": "test data"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - DELETE
    [Documentation]    Test HTTP connector with DELETE request
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
    ${response}=    Execute Command    api    /delete    options={"method": "DELETE"}
    Should Be Equal As Numbers    ${response.status_code}    200
    Close Session    api

Test HTTP Connector - Custom Headers
    [Documentation]    Test HTTP connector with custom headers
    Open Session    api    http    http    ${API_HOST}    ${API_PORT}    protocol=https    
    ${headers}=    Create Dictionary    X-Custom-Header=CustomValue
    ${response}=    Execute Command    api    /headers    options={"method": "GET", "headers": ${headers}}
    Should Contain    ${response.text}    X-Custom-Header
    Close Session    api

Test HTTP Connector - HTTP Protocol
    [Documentation]    Test HTTP connector with HTTP (not HTTPS)
    Open Session    api    http    http    ${API_HOST}    80    protocol=http    
    ${response}=    Execute Command    api    /get    options={"method": "GET"}
    Should Not Be Empty    ${response.text}
    Close Session    api

