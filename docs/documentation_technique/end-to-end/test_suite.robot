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

[Setup]             Run Keywords            Open Browser                    ${GEOCONTRIB _URL}
...                 AND                     Maximize Browser Window
...                 AND                     Set Selenium Speed              ${SELSPEED}

Connect GeoContrib - TEST 5
    Current Frame Should Contain            Se Connecter
    Geocontrib Connect Superuser            ${SUPERUSERNAME}                ${SUPERUSERPASSWORD}
    Page Should Contain                     ${SUPERUSERDISPLAYNAME}

Create Project with Random Projectname - TESTS 10, 17
    Page Should Not Contain                 ${RANDOMPROJECTNAME}
    Geocontrib Create Project               ${RANDOMPROJECTNAME}
    Page Should Contain                     ${RANDOMPROJECTNAME}

Create Feature Types with Random Featuretypename - TEST 97
    Page Should Not Contain                 ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}#2
    Page Should Contain                     ${RANDOMFEATURETYPENAME}

Create Features with Random Featurename on Random Coordinates - TEST 117
    Page Should Not Contain                 ${RANDOMFEATURENAME}
    Geocontrib Create Feature               ${RANDOMFEATURETYPENAME}        ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates         ${X1}                           ${Y1}
    Page Should Contain                     ${RANDOMFEATURENAME}

# TODO: à remplacer par get page
    Click Element       xpath=//html/body/header/div/div/div[1]
    Click Element       xpath=//html/body/header/div/div/div[1]/div/a[1]

    Page Should Not Contain                 ${RANDOMFEATURENAME}#2
    Geocontrib Create Feature               ${RANDOMFEATURETYPENAME}        ${RANDOMFEATURENAME}#2
    Geocontrib Click At Coordinates         ${X2}                           ${Y2}
    Page Should Contain                     ${RANDOMFEATURENAME}#2

Search for drafts - TEST 168
    Geocontrib Draft Search Map             ${RANDOMPROJECTNAME}
    Geocontrib Draft Search List            ${RANDOMPROJECTNAME}
    Page Should Contain                     ${RANDOMFEATURENAME}

Create Layer - ADMIN
    Geocontrib Create Layer                 ${ADMIN_URL}            ${LAYER1_TITLE}         ${LAYER1_URL}           ${LAYER1_TYPE}          ${LAYER1_OPTIONS}            
    Geocontrib Create Layer                 ${ADMIN_URL}            ${LAYER2_TITLE}         ${LAYER2_URL}           ${LAYER2_TYPE}          ${LAYER2_OPTIONS}            
    Page Should Contain                     ${LAYER1_TITLE}         ${LAYER2_URL}

Create Basemap - TESTS 78, 79, 88, 
    Geocontrib Create Basemap               ${GEOCONTRIB_URL}       ${BASEMAPNAME}          ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}         ${LAYER1_URL}           ${LAYER1_TYPE}           ${LAYER2_TITLE}           ${LAYER2_URL}           ${LAYER2_TYPE}
    # Page Should Contain                     ${BASEMAPNAME}

Edit Featuretype - TEST NA
    Geocontrib Edit Featuretype             ${RANDOMFEATURETYPENAME}      ${FEATURETYPEEDITION}
    Page Should Contain                     ${FEATURETYPEEDITION}

# Export GeoJson
#     Geocontrib Json Export                  ${RANDOMPROJECTNAME}${PROJECTEDITION}      ${RANDOMFEATURETYPENAME}       ${FEATURETYPEEDITION}
#     # Page Should Contain     

# Import GeoJson
#     Geocontrib Json Import
#     # Page Should Contain     

# [Teardown]    Run Keywords                    Geocontrib Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
# ...                           AND             Geocontrib Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
# ...                           AND             Geocontrib Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
# ...                           AND             Sleep     3
# ...                           AND             Close Browser