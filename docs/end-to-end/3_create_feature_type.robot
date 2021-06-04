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

*** Test Cases ***

[Setup]     Run Keywords    Open Browser ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed ${SELSPEED}
...         AND             Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
...         AND             Geocontrib Create Project  ${RANDOMPROJECTNAME}


Create Feature Types with Random Featuretypename
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}#2
    # Page Should Contain     ${RANDOMFEATURETYPENAME}



# [Teardown]    Close Browser