*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1

${RANDOMPROJECTNAME}   ${{ "projet - {}".format(datetime.datetime.now()) }}
${RANDOMFEATURETYPENAME}    ${{ "type - {}".format(datetime.datetime.now()) }}
${RANDOMFEATURENAME}    ${{ "signalement - {}".format(datetime.datetime.now()) }}

*** Test Cases ***

[Setup]     Run Keywords    Open Browser ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed ${SELSPEED}
...         AND             Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
...         AND             Geocontrib Create Project  ${RANDOMPROJECTNAME}
...         AND             Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}
...         AND             Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}#2

Create Feature #1 with Random Featurename on Random Coordinates
    ${X}    Set Variable    ${{ random.randint(1, 50) }}
    ${Y}    Set Variable    ${{ random.randint(1, 50) }}
    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
    Click Element    xpath=//button[@type='submit']
    # Page Should Contain     ${RANDOMFEATURENAME}

Back to Project Page
    Click Element    xpath=//html/body/header/div/div/div[1]
    Click Element    xpath=//html/body/header/div/div/div[1]/div/a[1]

Create Feature #2 with Random Featurename on Random Coordinates

    ${X}    Set Variable    ${{ random.randint(1, 30) }}
    ${Y}    Set Variable    ${{ random.randint(1, 30) }}
    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
    Click Element    xpath=//button[@type='submit']
    # Page Should Contain     ${RANDOMFEATURENAME}

# [Teardown]   Run Keywords     Close Browser