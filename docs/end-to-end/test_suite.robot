*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  ./library/GeoConnectLibrary.py
Library  ./library/GeoCreateLibrary.py
Library  ./library/GeoDeleteLibrary.py
Library  ./library/GeoJson.py


*** Variables ***

# TODO: mettre ces variables dans un fichier à part, qui ira dans gitignore
${URL}  https://geocontrib.dev.neogeo.fr
${ADMINURL}  https://geocontrib.dev.neogeo.fr/admin
${SUPERUSERNAME}    [CHANGE ME]
${SUPERUSERPASSWORD}    [CHANGE ME]

${RANDOMPROJECTNAME}   ${{ "{}eme projet".format(random.randint(1, 1000)) }}
${RANDOMFEATURETYPENAME}    ${{ "{}eme type".format(random.randint(1, 1000)) }}
${RANDOMFEATURENAME}    ${{ "{}eme signalement".format(random.randint(1, 1000)) }}


*** Test Cases ***

[Setup]  Open Browser  ${URL}

Connect GeoContrib
    Geo Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}

Create Project with Random Projectname
    Geo Create Project  ${RANDOMPROJECTNAME}

Create Feature Type with Random Featuretypename
    Geo Create Featuretype  ${RANDOMFEATURETYPENAME}

Create Feature with Random Featurename
    ${X}    Generate Random String    2    [NUMBERS]
    ${Y}    Generate Random String    2    [NUMBERS]
    Geo Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
    Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
    Click Element    xpath=//button[@type='submit']

# TODO
# Export GeoJson
#     Geo Json Export

# TODO
# Import GeoJson
#     Geo Json Import

[Teardown]   Run Keywords    Geo Delete Feature  ${RANDOMFEATURENAME}   ${ADMINURL}
...          AND             Geo Delete Featuretype  ${RANDOMFEATURETYPENAME}   ${ADMINURL}
...          AND             Geo Delete Project  ${RANDOMPROJECTNAME}   ${ADMINURL}
...          AND             Sleep     3
...          AND             Close Browser