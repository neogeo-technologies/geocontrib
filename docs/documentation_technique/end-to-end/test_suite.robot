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

[Setup]             Run Keywords            Open Browser                    ${GEOCONTRIB _URL}      ${BROWSER_NAME}
...                 AND                     Maximize Browser Window
...                 AND                     Set Selenium Speed              ${SELSPEED}

Connect GeoContrib - TEST 7
    Current Frame Should Contain            Se Connecter
    Geocontrib Connect Superuser            ${SUPERUSERNAME}                ${SUPERUSERPASSWORD}
    Page Should Contain                     ${SUPERUSERDISPLAYNAME}

Create Project with Random Projectname - TESTS 10, 17
    #correspond au test 10, mais pas le 17
    Page Should Not Contain                 ${RANDOMPROJECTNAME}
    Geocontrib Create Project               ${RANDOMPROJECTNAME}
    #Wait Until Page Does Not Contain         Projet en cours de création. Vous allez être redirigé. 
    # attendre le changement de page
    Wait Until Location Does Not Contain    /creer-projet
    Page Should Contain                     ${RANDOMPROJECTNAME}
    # Vérifier que le projet est modéré (à améliorer)
    Page Should Contain                     Oui
    # Vérifier que la visibilité est à Utilisateur anonyme (à améliorer, ne vérifie pas les 2 visibilités)
    Page Should Contain                     Utilisateur anonyme
    # Vérifier que le signalement a une description (à améliorer: utilisé une variable)
    Page Should Contain                     Exemple de description
    # Le test ci-dessus ne permet pas de vérifier que le projet a été créé, car la page de création contient le nom du projet,
    # si la validation du formulaire plante, le test reste en suspend et ne déclenche pas d'erreur, il faudrait vérifier qu'il n'y a pas de message d'erreur peut-être

Edit Project with Random Projectname - TESTS 74, ...
    # Start from main page
    From Main Page To Project Page
    # Test 74 | enter modify mode
    Geocontrib Edit Project                 ${RANDOMPROJECTNAME}        ${PROJECTEDITION}
    Page Should Contain                     ${PROJECTEDITION}
    # Vérifier que le projet est modéré (à améliorer)
    Page Should Contain                     Non
    # Vérifier que la visibilité est à Utilisateur anonyme (à améliorer, ne vérifie pas les 2 visibilités)
    Page Should Contain                     Utilisateur connecté
    # Vérifier que le signalement a une description (à améliorer: ajouter une variable spécifique à la description)
    Page Should Contain                     ${PROJECTEDITION}

Create Feature Type with Random Featuretypename - TEST 97
    Page Should Not Contain                 ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    # attendre que le loader disparaissent ! NE MARCHE PAS
    #Wait Until Page Does Not Contain         Récupération des types de signalements en cours... 
    #Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}#2
    Page Should Contain                     ${RANDOMFEATURETYPENAME}

Edit Feature Type - TEST n°?
    Page Should Contain                     ${RANDOMFEATURETYPENAME}
    Geocontrib Edit Featuretype             ${RANDOMFEATURETYPENAME}        ${FEATURETYPEEDITION}
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    Page Should Contain                     ${FEATURETYPEEDITION}

Create Feature with Random Featurename on Random Coordinates - TEST 117
    Page Should Not Contain                 ${RANDOMFEATURENAME}
    Geocontrib Create Feature               ${RANDOMFEATURETYPENAME}        ${RANDOMFEATURENAME}
    Geocontrib Click At Coordinates         ${X1}                           ${Y1}                       ${BROWSER_NAME}
    Geocontrib Click Save Changes
    Page Should Contain                     ${RANDOMFEATURENAME}
    # Vérifier que le signalement a une description (à améliorer: utilisé une variable)
    Page Should Contain                     Exemple de description

Edit Feature - TEST n°?
    # depuis la page de détail du signalement juste créé
    Page Should Contain                     ${RANDOMFEATURENAME}
    Geocontrib Edit Feature                 ${RANDOMFEATURETYPENAME}        ${FEATUREEDITION}
    Geocontrib Click Save Changes
    Page Should Contain                     ${FEATUREEDITION}
    # Vérifier que le signalement a le statut 'publié (à améliorer)
    Page Should Contain                     Publié
    # Vérifier que le signalement a une description (à améliorer)
    #Page Should Contain                     ${FEATUREEDITION}


#Search for drafts - TEST 168
#    Geocontrib Draft Search Map             ${RANDOMPROJECTNAME}
#    Geocontrib Draft Search List            ${RANDOMPROJECTNAME}
#    Page Should Contain                     ${RANDOMFEATURENAME}
#
#Create Layer - ADMIN
#    Geocontrib Create Layer                 ${ADMIN_URL}            ${LAYER1_TITLE}         ${LAYER1_URL}           ${LAYER1_TYPE}          ${LAYER1_OPTIONS}            
#    Geocontrib Create Layer                 ${ADMIN_URL}            ${LAYER2_TITLE}         ${LAYER2_URL}           ${LAYER2_TYPE}          ${LAYER2_OPTIONS}            
#    Page Should Contain                     ${LAYER1_TITLE}         ${LAYER2_URL}
#
#Create Basemap - TESTS 78, 79, 88, 
#    Geocontrib Create Basemap               ${GEOCONTRIB_URL}       ${BASEMAPNAME}          ${RANDOMPROJECTNAME}    ${LAYER1_TITLE}         ${LAYER1_URL}           ${LAYER1_TYPE}           ${LAYER2_TITLE}           ${LAYER2_URL}           ${LAYER2_TYPE}
#    # Page Should Contain                     ${BASEMAPNAME}
#
# Export GeoJson
#     Geocontrib Json Export                  ${RANDOMPROJECTNAME}${PROJECTEDITION}      ${RANDOMFEATURETYPENAME}       ${FEATURETYPEEDITION}
#     # Page Should Contain     

# Import GeoJson
#     Geocontrib Json Import
#     # Page Should Contain     

[Teardown]
    From Main Page To Project Page
    Geocontrib Delete Project  
    Run Keywords                                Sleep       3
...                             AND             Close Browser


*** Keywords ***
From Main Page To Project Page
    Geocontrib Go To Main Page                  ${GEOCONTRIB_URL}
    Wait Until Page Does Not Contain            En cours de chargement ... 
    Geocontrib Search Project                   ${RANDOMPROJECTNAME}
    Wait Until Element Is Not Visible           css:div.ui > div.ui.inverted.dimmer.active
    Geocontrib Click On Project                 ${RANDOMPROJECTNAME}
    Wait Until Page Does Not Contain            Projet en cours de chargement ... 