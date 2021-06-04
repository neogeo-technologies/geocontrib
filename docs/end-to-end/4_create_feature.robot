*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py

Variables   library/tests_settings.py
Variables   library/project_settings.py
Variables   library/coordinates_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}
...         AND             Geocontrib Connect Superuser        ${SUPERUSERNAME}    ${SUPERUSERPASSWORD}
...         AND             Geocontrib Create Project           ${RANDOMPROJECTNAME}
...         AND             Geocontrib Create Featuretype       ${RANDOMFEATURETYPENAME}



Create Feature #1 with Random Featurename on Random Coordinates
    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates     ${X1}  ${Y1}
    # Page Should Contain     ${RANDOMFEATURENAME}

Back to Project Page
    Click Element    xpath=//html/body/header/div/div/div[1]
    Click Element    xpath=//html/body/header/div/div/div[1]/div/a[1]

Create Feature #2 with Random Featurename on Random Coordinates

    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates     ${X2}  ${Y2}
    # Page Should Contain     ${RANDOMFEATURENAME}

# [Teardown]   Run Keywords     Close Browser