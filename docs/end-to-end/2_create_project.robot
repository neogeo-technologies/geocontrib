*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py
Library  library/GeoBasemapLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1

${RANDOMPROJECTNAME}   ${{ "projet - {}".format(datetime.datetime.now()) }}

${LAYER1_TITLE}          PIGMA Occupation du sol
${LAYER1_URL}            https://www.pigma.org/geoserver/asp/wms?
${LAYER1_TYPE}           WMS
${LAYER1_OPTIONS}    {
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
${LAYER2_TYPE}           TMS
${LAYER2_OPTIONS}    {
...                         "maxZoom": 20,
...                         "attribution": "\u00a9 les contributeurs d\u2019OpenStreetMap"
...                      }

${BASEMAPNAME}          ${{ "fond carto - {}".format(datetime.datetime.now()) }}

*** Test Cases ***

[Setup]     Run Keywords    Open Browser ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed ${SELSPEED}
...         AND             Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}

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