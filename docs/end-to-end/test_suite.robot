*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeocontribConnectLibrary.py
Library  library/GeocontribCreateLibrary.py
Library  library/GeocontribSearchLibrary.py
Library  library/GeocontribBasemapLibrary.py
Library  library/GeocontribJsonLibrary.py
Library  library/GeocontribDeleteLibrary.py
Library  library/GeocontribEditLibrary.py
Library  library/GeocontribOnCoordinatesLibrary.py

Variables   library/tests_settings.py
Variables   library/project_settings.py
Variables   library/layers_settings.py
Variables   library/coordinates_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]     Run Keywords    Open Browser                        ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed                  ${SELSPEED}

Connect GeoContrib - Test 4
    Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
    # Frame Should Not Contain    Se connecter

Create Project with Random Projectname - Tests 10, 17
    Geocontrib Create Project  ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMPROJECTNAME}

Create Feature Types with Random Featuretypename - Test 97
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}#2
    # Page Should Contain     ${RANDOMFEATURETYPENAME}

Create Feature #1 with Random Featurename on Random Coordinates - Test 117

    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates     ${X1}  ${Y1}
    # Page Should Contain     ${RANDOMFEATURENAME}

Back to Project Page
    Click Element    xpath=//html/body/header/div/div/div[1]
    Click Element    xpath=//html/body/header/div/div/div[1]/div/a[1]

Create Feature #2 with Random Featurename on Random Coordinates - Test 117

    Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates     ${X2}  ${Y2}
    # Page Should Contain     ${RANDOMFEATURENAME}

Search for drafts - Test 168
    Geocontrib Draft Search List      ${RANDOMPROJECTNAME}
    Geocontrib Draft Search Map       ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMFEATURENAME}

Create Layer - ADMIN
    Geocontrib Create Layer      ${ADMIN_URL}      ${LAYER1_TITLE}       ${LAYER1_URL}     ${LAYER1_TYPE}     ${LAYER1_OPTIONS}            
    Geocontrib Create Layer      ${ADMIN_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}     ${LAYER2_TYPE}     ${LAYER2_OPTIONS}            
    # Page Should Contain      ${LAYER1_TITLE}       ${LAYER2_URL}

Create Basemap - Tests 78, 79, 88, 
    Geocontrib Create Basemap    ${GEOCONTRIB_URL}        ${BASEMAPNAME}      ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}       ${LAYER1_URL}      ${LAYER1_TYPE}     ${LAYER2_TITLE}       ${LAYER2_URL}     ${LAYER2_TYPE}
    # Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

Query Basemap - Test 89
    Geocontrib Query Basemap   ${GEOCONTRIB _URL}      ${RANDOMPROJECTNAME}
    # Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

Edit Project - Test NA
    Geocontrib Edit Project      ${GEOCONTRIB_URL}      ${RANDOMPROJECTNAME}        ${PROJECTEDITION}
    # Page Should Contain        ${PROJECTEDITION}

Edit Feature - Test NA (D. Modification d'un projet)
    Geocontrib Edit Feature      ${RANDOMFEATURENAME}        ${FEATUREEDITION}
    # Page Should Contain        ${FEATUREEDITION}

Edit Featuretype - Test NA
    Geocontrib Edit Featuretype      ${RANDOMFEATURETYPENAME}      ${FEATURETYPEEDITION}
    # Page Should Contain         ${FEATURETYPEEDITION}

# Export GeoJson
#     Geocontrib Json Export  ${RANDOMPROJECTNAME}${PROJECTEDITION}      ${RANDOMFEATURETYPENAME}       ${FEATURETYPEEDITION}
#     # Page Should Contain     

# Import GeoJson
#     Geocontrib Json Import
#     # Page Should Contain     

# [Teardown]    Run Keywords                    Geocontrib Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
# ...                           AND             Geocontrib Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
# ...                           AND             Geocontrib Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
# ...                           AND             Sleep     3
# ...                           AND             Close Browser