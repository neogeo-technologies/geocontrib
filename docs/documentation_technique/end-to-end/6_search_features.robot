*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py
Library  library/GeoSearchLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}
...         AND             Geocontrib Connect Superuser        ${SUPERUSERNAME}    ${SUPERUSERPASSWORD}
...         AND             Geocontrib Create Project           ${RANDOMPROJECTNAME}
...         AND             Geocontrib Create Featuretype       ${RANDOMFEATURETYPENAME}
...         AND             Geocontrib Create Feature           ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
...         AND             Geocontrib Click At Coordinates     ${X1}  ${Y1}

Search for drafts
    Geocontrib Draft Search      ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMFEATURENAME}

# [Teardown]     Close Browser