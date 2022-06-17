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
    Find Project
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
    Find Project
    Go To Project Page
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
    # Start from main page
    Find Project
    Go To Project Page
    Page Should Not Contain                 ${RANDOMFEATURETYPENAME}
    Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}        Point
    Click Button                            send-feature_type
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

Create Feature Type with Random Featuretypename With Geometry Type Polygone
    # Start from main page
    Find Project
    Go To Project Page

    Page Should Not Contain                 ${RANDOMFEATURETYPENAME}-Polygone
    Geocontrib Create Featuretype           ${RANDOMFEATURETYPENAME}-Polygone    Polygone
    Geocontrib Add Custom Fields            ${SYMBONAMELIST}    ${SYMBONAMECHAR}    ${SYMBONAMEBOOL}    ${SYMBOPTIONLIST}
    Click Button                            send-feature_type
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    Page Should Contain                     ${RANDOMFEATURETYPENAME}-Polygone

Edit Feature Type Default Symbology
    # Start from main page
    Find Project
    Go To Project Page

    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Geocontrib Edit Featuretype Symbology       ${SYMBOLCOLORCODE}   ${SYMBOLOPACITY}   .default
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    #*Validate color value 
    Element Attribute Value Should Be           css:div.default #couleur         value        ${SYMBOLCOLORCODE}
    #*Validate opacity value
    Element Attribute Value Should Be           css:div.default #opacity         value        ${SYMBOLOPACITY}


Edit Custom Field Symbology For List
    # Start from main page
    Find Project
    Go To Project Page

    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    #*Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMELIST}  ${SYMBOPTIONLIST}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[0]} #couleur         value        ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[0]} #opacity         value        ${SYMBOPTIONOPACITYLIST[0]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[1]} #couleur         value        ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[1]} #opacity         value        ${SYMBOPTIONOPACITYLIST[1]}

Edit Custom Field Symbology For Character Chain
    # Start from main page
    Find Project
    Go To Project Page

    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    #*Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMECHAR}  ${NONE}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div[id="Vide"] #couleur         value        ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div[id="Vide"] #opacity         value        ${SYMBOPTIONOPACITYLIST[0]}
    #* selector with space in ID doesn't work 
    Element Attribute Value Should Be           css:div[id^="Non"] #couleur         value        ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div[id^="Non"] #opacity         value        ${SYMBOPTIONOPACITYLIST[1]}

Edit Custom Field Symbology For Boolean
    # Start from main page
    Find Project
    Go To Project Page

    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    #*Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMEBOOL}  ${NONE}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${RANDOMFEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div[id="Décoché"] #couleur      value       ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div[id="Décoché"] #opacity      value       ${SYMBOPTIONOPACITYLIST[0]}
    Element Attribute Value Should Be           css:div[id="Coché"] #couleur        value       ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div[id="Coché"] #opacity        value       ${SYMBOPTIONOPACITYLIST[1]}


[Teardown]
    Find Project
    Go To Project Page
    Geocontrib Delete Project  
    Run Keywords                                Sleep       3
...                             AND             Close Browser


*** Keywords ***
Find Project
    Geocontrib Go To Main Page                  ${GEOCONTRIB_URL}
    Wait Until Page Does Not Contain            En cours de chargement ... 
    Geocontrib Search Project                   ${RANDOMPROJECTNAME}
    Wait Until Element Is Not Visible           css:div.ui > div.ui.inverted.dimmer.active

Go To Project Page
    Geocontrib Click On Project                 ${RANDOMPROJECTNAME}
    Wait Until Page Does Not Contain            Projet en cours de chargement ... 