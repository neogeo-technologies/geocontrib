*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeocontribConnectLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}

Connect GeoContrib
    Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
    # Frame Should Not Contain    Se connecter

    # [Teardown]   Run Keywords    Geocontrib Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
    # ...                            AND             Geocontrib Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
    # ...                            AND             Geocontrib Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
    # ...                            AND             Sleep     3
    # ...                            AND             Close Browser
