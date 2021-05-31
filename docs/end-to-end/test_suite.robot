*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py
Library  library/GeoSearchLibrary.py
Library  library/GeoBasemapLibrary.py
Library  library/GeoJsonLibrary.py
Library  library/GeoDeleteLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${RANDOMPROJECTNAME}   ${{ "{}eme projet".format(random.randint(1, 1000)) }}
${RANDOMFEATURETYPENAME}    ${{ "{}eme type".format(random.randint(1, 1000)) }}
${RANDOMFEATURENAME}    ${{ "{}eme signalement".format(random.randint(1, 1000)) }}

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

${BASEMAPNAME1}          ${{ "{}eme fond cartographique".format(random.randint(1, 1000)) }}
${BASEMAPNAME2}          ${{ "{}eme fond cartographique".format(random.randint(1, 1000)) }}

*** Test Cases ***

[Setup]  Run Keywords  Open Browser  ${GEOCONTRIB _URL}
...              AND   Set Selenium Speed  ${SELSPEED}

Connect GeoContrib
    Geo Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
    Frame Should Not Contain    Se connecter

Create Project with Random Projectname
    Geo Create Project  ${RANDOMPROJECTNAME}
    Page Should Contain     ${RANDOMPROJECTNAME}

Create Feature Type with Random Featuretypename
    Geo Create Featuretype  ${RANDOMFEATURETYPENAME}
    Page Should Contain     ${RANDOMFEATURETYPENAME}

# Create Feature with Random Featurename
#     ${X}    Generate Random String    1    [NUMBERS]
#     ${Y}    Generate Random String    1    [NUMBERS]
#     Geo Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
#     Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
#     Click Element    xpath=//button[@type='submit']
#     Page Should Contain     ${RANDOMFEATURENAME}

# Search for drafts
#     Geo Draft Search      ${RANDOMPROJECTNAME}
#     Page Should Contain     ${RANDOMFEATURENAME}

# # TODO
# Create Layer
#     Geo Create Layer      ${ADMIN_URL}      ${LAYER1_TITLE}       ${LAYER1_URL}     ${LAYER1_DESCRIPTION}            
#     Geo Create Layer      ${ADMIN_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}     ${LAYER2_DESCRIPTION}            
#     Page Should Contain      ${LAYER1_TITLE}       ${LAYER2_URL}

# # TODO
# Create Basemap
#     Geo Create Basemap    ${ADMIN_URL}        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}       ${LAYER1_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}
#     Geo Create Basemap    ${ADMIN_URL}        ${BASEMAPNAME2}      ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}       ${LAYER1_URL}      ${LAYER2_TITLE}       ${LAYER2_URL}
#     Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

# TODO
Create Feature with Random Featurename but on Queryable Coordinates
    ${X}    
    ${Y}    
    Geo Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
    Click Element    xpath=//button[@type='submit']
    Page Should Contain     ${RANDOMFEATURENAME}

Query Basemap
    Geo Query Basemap
#     Page Should Contain        ${BASEMAPNAME1}      ${RANDOMPROJECTNAME}

# TODO
# Edit Project
#     Geo Edit Project
#     Page Should Contain 

# TODO
# Edit Featuretype
#     Geo Edit Featuretype
#     Page Should Contain 

# TODO
# Edit Feature
#     Geo Edit Feature
#     Page Should Contain 

# TODO
# Export GeoJson
#     Geo Json Export  ${RANDOMPROJECTNAME}
#     # Page Should Contain     

# TODO
# Import GeoJson
#     Geo Json Import
#     # Page Should Contain     

# [Teardown]   Run Keywords    Geo Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
# ...                            AND             Geo Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
# ...                            AND             Geo Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
# ...                            AND             Sleep     3
# ...                            AND             Close Browser