*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  ./library/GeoConnectLibrary.py
Library  ./library/GeoCreateLibrary.py
Library  ./library/GeoDeleteLibrary.py
Library  ./library/GeoJson.py

Variables   ./library/tests_settings.py


*** Variables ***

${RANDOMPROJECTNAME}   ${{ "{}eme projet".format(random.randint(1, 1000)) }}
${RANDOMFEATURETYPENAME}    ${{ "{}eme type".format(random.randint(1, 1000)) }}
${RANDOMFEATURENAME}    ${{ "{}eme signalement".format(random.randint(1, 1000)) }}


*** Test Cases ***

[Setup]  Open Browser  ${URL}

Connect GeoContrib
    Geo Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
    Page Should Not Contain    Se connecter

Create Project with Random Projectname
    Geo Create Project  ${RANDOMPROJECTNAME}
    Page Should Contain     ${RANDOMPROJECTNAME}

Create Feature Type with Random Featuretypename
    Geo Create Featuretype  ${RANDOMFEATURETYPENAME}
    Page Should Contain     ${RANDOMFEATURETYPENAME}

Create Feature with Random Featurename
    ${X}    Generate Random String    1    [NUMBERS]
    ${Y}    Generate Random String    1    [NUMBERS]
    Geo Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
    Click Element    xpath=//button[@type='submit']
    Page Should Contain     ${RANDOMFEATURENAME}

# TODO
# Export GeoJson
#     Geo Json Export  ${RANDOMPROJECTNAME}
#     # Page Should Contain     

# TODO
# Import GeoJson
#     Geo Json Import
#     # Page Should Contain     

[Teardown]   Run Keywords    Geo Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
...          AND             Geo Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
...          AND             Geo Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
...          AND             Sleep     3
...          AND             Close Browser