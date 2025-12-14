*** Settings ***
Name           vault

Library        Collections
Library        sysbot.Sysbot

*** Variables ***
# These would typically be set via environment or secret management in real usage
# These are example values - real tests would need a running Vault instance
${VAULT_URL}=         https://vault.example.com:8200
${VAULT_TOKEN}=       hvs.CAESI...example-token
${ENGINE_NAME}=       secret

*** Test Cases ***

Vault Plugin Is Loaded
    [Documentation]    Verify that the vault plugin is properly loaded and accessible
    [Tags]    vault    smoke
    # Simply verify we can call the plugin's method - it will return {} if vault isn't reachable
    ${result}=    Call Components    plugins.vault.dump_engine    fake_token    https://127.0.0.1:8200    fake_engine
    # If we got here without AttributeError, the plugin and method exist
    Should Be Equal As Strings    ${result.__class__.__name__}    dict

Dump Vault Engine Without Secret Storage
    [Documentation]    Test dumping a Vault engine and retrieving secrets directly
    [Tags]    vault    manual    requires-vault
    ${secrets}=    Call Components    plugins.vault.dump_engine    ${VAULT_TOKEN}    ${VAULT_URL}    ${ENGINE_NAME}
    Should Be Equal As Strings    ${secrets.__class__.__name__}    dict
    Log    Retrieved secrets: ${secrets}

Dump Vault Engine With Secret Storage
    [Documentation]    Test dumping a Vault engine and storing in secret manager
    [Tags]    vault    manual    requires-vault
    ${result}=    Call Components    plugins.vault.dump_engine    ${VAULT_TOKEN}    ${VAULT_URL}    ${ENGINE_NAME}    key=vault_secrets
    Should Be Equal As Strings    ${result}    Imported
    
    # Verify secrets are stored and accessible
    ${secret}=    Get Secret    vault_secrets
    Should Not Be Empty    ${secret}

Dump Vault Engine And Access Nested Secret
    [Documentation]    Test accessing a nested secret after dumping
    [Tags]    vault    manual    requires-vault
    Call Components    plugins.vault.dump_engine    ${VAULT_TOKEN}    ${VAULT_URL}    ${ENGINE_NAME}    key=vault_data
    
    # Access nested secret using dot notation
    # Assuming there's a secret path "myapp/config" with a key "database_url"
    ${db_url}=    Get Secret    vault_data.myapp/config.database_url
    Should Not Be Empty    ${db_url}

Handle Invalid Vault URL
    [Documentation]    Test error handling for invalid Vault URL
    [Tags]    vault    error-handling    manual    requires-vault
    Run Keyword And Expect Error    RuntimeError: *    
    ...    Call Components    plugins.vault.dump_engine    ${VAULT_TOKEN}    https://invalid-vault.example.com:8200    ${ENGINE_NAME}

Handle Invalid Token
    [Documentation]    Test error handling for invalid authentication token
    [Tags]    vault    error-handling    manual    requires-vault
    Run Keyword And Expect Error    RuntimeError: *
    ...    Call Components    plugins.vault.dump_engine    invalid_token    ${VAULT_URL}    ${ENGINE_NAME}
