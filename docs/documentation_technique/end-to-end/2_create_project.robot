*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeocontribConnectLibrary.py
Library  library/GeocontribCreateLibrary.py
Library  library/GeocontribBasemapLibrary.py

Variables   library/tests_settings.py
Variables   library/project_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}
...         AND             Geocontrib Connect Superuser        ${SUPERUSERNAME}    ${SUPERUSERPASSWORD}

Create Project with Random Projectname
    Geocontrib Create Project  ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMPROJECTNAME}

Create Layer
    Geocontrib Create Layer      ${ADMIN_URL}      ${LAYER1_TITLE}       ${LAYER1_URL}     ${LAYER1_DESCRIPTION}            
    Geocontrib Create Layer      ${ADMIN_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}     ${LAYER2_DESCRIPTION}            
    # Page Should Contain      ${LAYER1_TITLE}       ${LAYER2_URL}

Create Basemap
    Geocontrib Create Basemap    ${ADMIN_URL}        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}    ${LAYERS}
    Geocontrib Create Basemap    ${ADMIN_URL}        ${BASEMAPNAME2}      ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}       ${LAYER1_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}
    # Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

Query Basemap
    Geocontrib Query Basemap   ${GEOCONTRIB _URL}      ${RANDOMPROJECTNAME}
    # Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

# [Teardown]    Close Browser
