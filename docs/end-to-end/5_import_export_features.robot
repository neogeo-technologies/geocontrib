*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeoConnectLibrary.py
Library  library/GeoCreateLibrary.py
Library  library/GeoJsonLibrary.py

Variables   library/tests_settings.py


*** Variables ***

${SELSPEED}     0.1

${RANDOMPROJECTNAME}   ${{ "projet - {}".format(datetime.datetime.now()) }}
${RANDOMFEATURETYPENAME}    ${{ "type - {}".format(datetime.datetime.now()) }}
${RANDOMFEATURENAME}    ${{ "signalement - {}".format(datetime.datetime.now()) }}

*** Test Cases ***

[Setup]     Run Keywords    Open Browser ${GEOCONTRIB _URL}
...         AND             Maximize Browser Window
...         AND             Set Selenium Speed ${SELSPEED}
...         AND             Geocontrib Connect Superuser  ${SUPERUSERNAME}  ${SUPERUSERPASSWORD}
...         AND             Geocontrib Create Project  ${RANDOMPROJECTNAME}
...         AND             Geocontrib Create Featuretype  ${RANDOMFEATURETYPENAME}
...         AND             ${X}    Set Variable    ${{ random.randint(1, 50) }}
...         AND             ${Y}    Set Variable    ${{ random.randint(1, 50) }}
...         AND             Geocontrib Create Feature  ${RANDOMFEATURETYPENAME}  ${RANDOMFEATURENAME}
...         AND             Click Element At Coordinates       xpath=//div[@id='map']/div/div[4]/div     ${X}  ${Y}
...         AND             Click Element    xpath=//button[@type='submit']


# Export GeoJson
#     Geocontrib Json Export  ${RANDOMPROJECTNAME}      ${RANDOMFEATURETYPENAME}
#     # Page Should Contain     

# Import GeoJson
#     Geocontrib Json Import
#     # Page Should Contain     

# [Teardown]    Close Browser