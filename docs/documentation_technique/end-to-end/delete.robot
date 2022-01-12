*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeocontribConnectLibrary.py
Library  library/GeocontribDeleteLibrary.py

Variables   library/tests_settings.py
Variables   library/project_settings.py
Variables   library/layers_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}
...         AND             Geocontrib Connect Superuser        ${SUPERUSERNAME}    ${SUPERUSERPASSWORD}

# Delete Feature
#     Geocontrib Delete Feature       ${ADMINURL}     ${RANDOMFEATURENAME}

# Delete Featuretype
#     Geocontrib Delete Featuretype   ${ADMINURL}     ${RANDOMFEATURETYPENAME}

# Delete Project
#     Geocontrib Delete Project       ${ADMINURL}     ${RANDOMPROJECTNAME}

Delete Layer
    Geocontrib Delete Layer         ${ADMINURL}     ${LAYER1_TITLE}     ${LAYER1_URL}     ${LAYER1_TYPE}
    Geocontrib Delete Layer         ${ADMINURL}     ${LAYER2_TITLE}     ${LAYER2_URL}     ${LAYER2_TYPE}

# [Teardown]        Close Browser