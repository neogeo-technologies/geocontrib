*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py
Library  library/GeoSearchLibrary.py
Library  library/GeoBasemapLibrary.py
Library  library/GeoJsonLibrary.py
Library  library/GeoDeleteLibrary.py
Library  library/GeoEditLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1

${RANDOMPROJECTNAME}   ${{ "{}eme projet".format(random.randint(1, 10000)) }}
${RANDOMFEATURETYPENAME}    ${{ "{}eme type".format(random.randint(1, 10000)) }}
${RANDOMFEATURENAME}    ${{ "{}eme signalement".format(random.randint(1, 10000)) }}

${PROJECTEDITION}    - projet édité
${FEATURETYPEEDITION}    - type édité
${FEATUREEDITION}    - signalement édité

${LAYER1}       1er attribut     2e attriut     3e attribut

${LAYER1_TITLE}          PIGMA Occupation du sol
${LAYER1_URL}            https://www.pigma.org/geoserver/asp/wms?

${LAYER1_DESCRIPTION}    {
...                         \"format\": \"image/png\",
...                         \"layers\": \"asp_rpg_2012_047\",
...                         \"maxZoom\": 18,
...                         \"minZoom\": 7,
...                         \"opacity\": 0.8,
...                         \"attribution\": \"PIGMA\",
...                         \"transparent\": true
...                      }

${LAYER2_TITLE}          OpenStreetMap France
${LAYER2_URL}            https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png

${LAYER2_DESCRIPTION}    {
...                         "maxZoom": 20,
...                         "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap"
...                      }

${BASEMAPNAME1}          ${{ "{}eme fond cartographique".format(random.randint(1, 10000)) }}
${BASEMAPNAME2}          ${{ "{}eme fond cartographique".format(random.randint(1, 10000)) }}

*** Test Cases ***

[Setup] Run Keywords Open Browser ${GeoCONTRIB _URL}
... AND Maximize Browser Window
... AND Set Selenium Speed ${SELSPEED}

Connect GeoContrib
    Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
    # Frame Should Not Contain    Se connecter

Create Project with Random Projectname
    Geocontrib Create Project  ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMPROJECTNAME}

Create Feature Types with Random Featuretypename
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}#2
    # Page Should Contain     ${RANDOMFEATURETYPENAME}

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

Search for drafts
    Geocontrib Draft Search      ${RANDOMPROJECTNAME}
    # Page Should Contain     ${RANDOMFEATURENAME}

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

Edit Project
    Geocontrib Edit Project      ${RANDOMPROJECTNAME}        ${PROJECTEDITION}
    # Page Should Contain        ${PROJECTEDITION}

Edit Feature
    Geocontrib Edit Feature      ${RANDOMFEATURENAME}        ${FEATUREEDITION}
#     Page Should Contain        ${FEATUREEDITION}

Edit Featuretype
    Geocontrib Edit Featuretype      ${RANDOMFEATURETYPENAME}      ${FEATURETYPEEDITION}
    # Page Should Contain         ${FEATURETYPEEDITION}

# Export GeoJson
#     Geocontrib Json Export  ${RANDOMPROJECTNAME}${PROJECTEDITION}      ${RANDOMFEATURETYPENAME}       ${FEATURETYPEEDITION}
#     # Page Should Contain     

# Import GeoJson
#     Geocontrib Json Import
#     # Page Should Contain     

# [Teardown]   Run Keywords    Geocontrib Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
# ...                            AND             Geocontrib Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
# ...                            AND             Geocontrib Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
# ...                            AND             Sleep     3
# ...                            AND             Close Browser