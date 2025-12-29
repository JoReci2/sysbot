# Polarion Integration Guide

This guide explains how to integrate Robot Framework test results with Siemens Polarion ALM/QA using SysBot's Polarion plugin.

## Overview

The Polarion plugin provides three main capabilities:

1. **Test Case Linking**: Link Robot Framework tests to Polarion test cases using tags
2. **xUnit Post-Processing**: Convert Robot Framework output to Polarion-compatible xUnit format
3. **Result Import**: Prepare results for import into Polarion

## 1. Linking Robot Framework Tests to Polarion STD

Use special tags in your Robot Framework test cases to establish links with Polarion Software Test Description (STD):

### Tag Format

- `polarion-id:TEST-XXX` - Links to Polarion test case ID (required for proper mapping)
- `polarion-title:Test Name` - Sets the Polarion test case title
- `polarion-{property}:{value}` - Custom Polarion properties

### Example Test Suite

```robot
*** Settings ***
Documentation    Login and Authentication Tests
...              This suite validates user authentication functionality
Metadata         Polarion-Project    MYPROJECT
Metadata         Polarion-Test-Suite    AUTH-SUITE

*** Test Cases ***

Valid User Login
    [Documentation]    Verify that a user can log in with valid credentials
    [Tags]    polarion-id:TEST-001
    ...       polarion-title:Valid User Login Test
    ...       polarion-priority:High
    ...       polarion-testEnvironment:Production
    Open Browser    ${LOGIN_URL}
    Input Text    username    valid_user
    Input Password    password    valid_pass
    Click Button    Login
    Page Should Contain    Welcome

Invalid Password Login
    [Documentation]    Verify that login fails with invalid password
    [Tags]    polarion-id:TEST-002
    ...       polarion-title:Invalid Password Test
    ...       polarion-priority:Medium
    ...       polarion-assignee:jdoe
    Open Browser    ${LOGIN_URL}
    Input Text    username    valid_user
    Input Password    password    invalid_pass
    Click Button    Login
    Page Should Contain    Invalid credentials

Password Reset Flow
    [Documentation]    Verify password reset functionality
    [Tags]    polarion-id:TEST-003
    ...       polarion-testEnvironment:Staging
    ...       smoke
    Open Browser    ${LOGIN_URL}
    Click Link    Forgot Password
    Input Text    email    user@example.com
    Click Button    Reset Password
    Page Should Contain    Email sent
```

### Supported Tag Properties

Common Polarion properties you can map via tags:

- `polarion-id` - Test case ID (required for mapping)
- `polarion-title` - Test case title
- `polarion-priority` - Test priority (High, Medium, Low)
- `polarion-testEnvironment` - Test environment
- `polarion-assignee` - Assigned user
- `polarion-status` - Test status
- `polarion-automation` - Automation status
- Any custom field defined in your Polarion project

## 2. Post-Processing with rebot for Polarion xUnit

After running your Robot Framework tests, convert the output to Polarion-compatible xUnit format.

### Using Python API

```python
from sysbot.plugins.polarion import generate_polarion_xunit

# Basic usage
generate_polarion_xunit(
    output_xml='output.xml',
    xunit_file='polarion_results.xml'
)

# With Polarion project and test run IDs
generate_polarion_xunit(
    output_xml='output.xml',
    xunit_file='polarion_results.xml',
    project_id='MYPROJECT',
    test_run_id='SPRINT-42-RUN-001'
)

# With custom properties
generate_polarion_xunit(
    output_xml='output.xml',
    xunit_file='polarion_results.xml',
    project_id='MYPROJECT',
    test_run_id='SPRINT-42-RUN-001',
    custom_properties={
        'environment': 'production',
        'version': '2.1.0',
        'build': '1234',
        'jenkins_job': 'nightly-tests'
    }
)
```

### Integration in CI/CD Pipeline

#### Jenkins Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Run Tests') {
            steps {
                sh 'robot --outputdir results tests/'
            }
        }
        
        stage('Generate Polarion xUnit') {
            steps {
                script {
                    sh """
                    python -c "
from sysbot.plugins.polarion import generate_polarion_xunit
generate_polarion_xunit(
    output_xml='results/output.xml',
    xunit_file='results/polarion_results.xml',
    project_id='${env.POLARION_PROJECT}',
    test_run_id='${env.BUILD_TAG}',
    custom_properties={
        'environment': '${env.ENVIRONMENT}',
        'build': '${env.BUILD_NUMBER}'
    }
)
                    "
                    """
                }
            }
        }
        
        stage('Upload to Polarion') {
            steps {
                // Upload polarion_results.xml to Polarion import directory
                sh 'cp results/polarion_results.xml /polarion/import/'
            }
        }
    }
}
```

#### GitLab CI Example

```yaml
stages:
  - test
  - report

test_job:
  stage: test
  script:
    - robot --outputdir results tests/
  artifacts:
    paths:
      - results/

polarion_export:
  stage: report
  dependencies:
    - test_job
  script:
    - |
      python -c "
      from sysbot.plugins.polarion import generate_polarion_xunit
      generate_polarion_xunit(
          output_xml='results/output.xml',
          xunit_file='results/polarion_results.xml',
          project_id='${POLARION_PROJECT}',
          test_run_id='${CI_PIPELINE_ID}',
          custom_properties={
              'environment': '${CI_ENVIRONMENT_NAME}',
              'branch': '${CI_COMMIT_REF_NAME}',
              'commit': '${CI_COMMIT_SHORT_SHA}'
          }
      )
      "
    # Upload to Polarion (method depends on your setup)
    - scp results/polarion_results.xml polarion-server:/import/
  artifacts:
    paths:
      - results/polarion_results.xml
```

## 3. Importing Results into Polarion

There are several methods to import the generated xUnit file into Polarion:

### Method 1: Manual Import via UI

1. Log into Polarion
2. Navigate to your project
3. Go to **Testing** → **Test Runs**
4. Select or create a test run
5. Click **Import Results**
6. Select **xUnit/JUnit XML**
7. Upload the `polarion_results.xml` file
8. Configure mapping options
9. Click **Import**

### Method 2: Scheduled xUnit Importer

Configure Polarion's scheduled xUnit file importer:

1. In Polarion, go to **Administration** → **Scheduled Jobs**
2. Create or edit an xUnit import job
3. Configure the import directory (e.g., `/polarion/import/`)
4. Set file pattern (e.g., `polarion_results*.xml`)
5. Configure project and template mappings
6. Set schedule (e.g., every 5 minutes)
7. Save and enable the job

Your CI/CD pipeline can then simply copy the xUnit file to this directory.

### Method 3: API Import with dump2polarion

For more control, use the `dump2polarion` tool:

```bash
# Install dump2polarion
pip install dump2polarion

# Upload results
dump2polarion \
    --user ${POLARION_USER} \
    --password ${POLARION_PASSWORD} \
    --xunit-file polarion_results.xml \
    --project-id MYPROJECT \
    --testrun-id SPRINT-42-RUN-001 \
    --polarion-url https://polarion.example.com
```

### Method 4: REST API

Use Polarion's REST API directly:

```python
import requests

url = "https://polarion.example.com/polarion/rest/v1/projects/MYPROJECT/testruns/RUN-001/import"
headers = {
    "Authorization": "Bearer YOUR_API_TOKEN",
    "Content-Type": "application/xml"
}

with open('polarion_results.xml', 'r') as f:
    xml_content = f.read()

response = requests.post(url, headers=headers, data=xml_content)
print(f"Import status: {response.status_code}")
```

## Best Practices

### 1. Test Case ID Management

- Use consistent ID format (e.g., `TEST-001`, `AUTH-001`)
- Ensure test case IDs exist in Polarion before running tests
- Use a naming convention that groups related tests

### 2. Tag Organization

```robot
*** Test Cases ***
My Test Case
    [Tags]    polarion-id:TEST-001              # Required for mapping
    ...       polarion-title:Descriptive Title   # Optional but recommended
    ...       polarion-priority:High             # Custom property
    ...       smoke                              # Regular RF tag
    ...       regression                         # Regular RF tag
```

Keep Polarion-specific tags first, followed by regular Robot Framework tags.

### 3. Metadata in Suite Settings

Add suite-level metadata for better organization:

```robot
*** Settings ***
Metadata    Polarion-Project        MYPROJECT
Metadata    Polarion-Iteration      Sprint-42
Metadata    Test-Type               Regression
```

### 4. CI/CD Integration

- Generate unique test run IDs (e.g., using build number or timestamp)
- Include build metadata in custom properties
- Archive xUnit files as build artifacts
- Set up automatic import to Polarion

### 5. Error Handling

```python
try:
    generate_polarion_xunit(
        output_xml='output.xml',
        xunit_file='polarion_results.xml',
        project_id='MYPROJECT'
    )
except FileNotFoundError:
    print("Error: output.xml not found")
    sys.exit(1)
except Exception as e:
    print(f"Error generating xUnit: {e}")
    sys.exit(1)
```

## Troubleshooting

### Tests Not Mapped to Polarion Test Cases

**Problem**: Tests appear as new test cases instead of linking to existing ones.

**Solution**: 
- Ensure `polarion-id` tags match exactly with Polarion test case IDs
- Verify test case IDs exist in Polarion before import
- Check Polarion importer configuration for ID field mapping

### Custom Properties Not Appearing

**Problem**: Custom properties defined in tags don't show up in Polarion.

**Solution**:
- Verify custom fields are defined in your Polarion project
- Check that field names match exactly (case-sensitive)
- Ensure Polarion importer is configured to read custom properties

### Import Fails with Authentication Error

**Problem**: Cannot import results due to authentication issues.

**Solution**:
- Verify Polarion credentials are correct
- Check API token hasn't expired
- Ensure user has permission to import test results
- Verify Polarion URL is correct

## Example Complete Workflow

```bash
# 1. Run Robot Framework tests with tags
robot --outputdir results tests/authentication/

# 2. Generate Polarion-compatible xUnit
python -c "
from sysbot.plugins.polarion import generate_polarion_xunit
generate_polarion_xunit(
    output_xml='results/output.xml',
    xunit_file='results/polarion_results.xml',
    project_id='AUTHPROJECT',
    test_run_id='SPRINT-42-AUTH',
    custom_properties={'environment': 'staging', 'tester': 'jenkins'}
)
"

# 3. Upload to Polarion import directory
cp results/polarion_results.xml /mnt/polarion/import/

# 4. Verify import (after scheduled job runs)
# Check Polarion UI or use API to verify results
```

## Additional Resources

- [Polarion Documentation](https://polarion.plm.automation.siemens.com/)
- [Robot Framework User Guide](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html)
- [dump2polarion GitHub](https://github.com/mkoura/dump2polarion)
- SysBot Documentation: [https://joreci2.github.io/sysbot/](https://joreci2.github.io/sysbot/)
