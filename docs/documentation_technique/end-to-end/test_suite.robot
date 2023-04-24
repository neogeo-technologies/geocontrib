*** Settings ***

Library  String
Library  SeleniumLibrary  75  5  run_on_failure=Nothing
Library  library/GeocontribUtilsLibrary.py
Library  library/GeocontribConnectLibrary.py
Library  library/GeocontribCreateLibrary.py
Library  library/GeocontribSearchLibrary.py
Library  library/GeocontribBasemapLibrary.py
Library  library/GeocontribJsonLibrary.py
Library  library/GeocontribDeleteLibrary.py
Library  library/GeocontribEditLibrary.py
Library  library/GeocontribOnCoordinatesLibrary.py
Library  library/GeocontribBrowseLibrary.py

Variables   library/tests_settings.py
Variables   library/project_settings.py
Variables   library/layers_settings.py
Variables   library/coordinates_settings.py


*** Variables ***

${SELSPEED}     0.1


*** Test Cases ***

[Setup]             Run Keywords            Open Browser                    ${GEOCONTRIB_URL}      ${BROWSER_NAME}
...                 AND                     Set Window Size                 1024    768
#...                 AND                     Maximize Browser Window
...                 AND                     Set Selenium Speed              ${SELSPEED}

Connect GeoContrib - TEST 7
    Wait Until Page Does Not Contain        En cours de chargement ...
    Current Frame Should Contain            Se Connecter
    Geocontrib Connect Superuser            ${SUPERUSERNAME}                ${SUPERUSERPASSWORD}
    Page Should Contain                     ${SUPERUSERDISPLAYNAME}

Create Project - TESTS 10, 17
    Find Project
    #correspond au test 10, mais pas le 17
    Page Should Not Contain                 ${PROJECTNAME}
    Geocontrib Create Project               ${PROJECTNAME}
    #Wait Until Page Does Not Contain         Projet en cours de création. Vous allez être redirigé. 
    # attendre le changement de page
    Wait Until Location Does Not Contain    /creer-projet
    Page Should Contain                     ${PROJECTNAME}
    # Vérifier que le projet est modéré (à améliorer)
    Page Should Contain                     Oui
    # Vérifier que la visibilité est à Utilisateur anonyme (à améliorer, ne vérifie pas les 2 visibilités)
    Page Should Contain                     Utilisateur anonyme
    # Vérifier que le signalement a une description (à améliorer: utiliser une variable)
    Page Should Contain                     Exemple de description
    # Le test ci-dessus ne permet pas de vérifier que le projet a été créé, car la page de création contient le nom du projet,
    # si la validation du formulaire plante, le test reste en suspend et ne déclenche pas d'erreur, il faudrait vérifier qu'il n'y a pas de message d'erreur peut-être


Edit Project - TESTS 74, ...
    # Start from main page
    Find Project
    Go To Project Page
    # enter modify mode
    Click Element                            id:edit-project
    Geocontrib Edit Project Title           ${PROJECTNAME}       ${PROJECTEDITION}
    Geocontrib Edit Project Description     ${PROJECTEDITION}
    Geocontrib Edit Project Visibilities
    Geocontrib Edit Project Options
    # submit the form
    Click Button                            id:send-project
    Page Should Contain                     ${PROJECTEDITION}
    # Vérifier que le projet est modéré (à améliorer)
    Page Should Contain                     Non
    # Vérifier que la visibilité est à Utilisateur anonyme (à améliorer, ne vérifie pas les 2 visibilités)
    Page Should Contain                     Utilisateur connecté
    # Vérifier que le signalement a une description (à améliorer: ajouter une variable spécifique à la description)
    Page Should Contain                     ${PROJECTEDITION}


Edit Project with Markdown Description
    # Start from main page
    Find Project
    Go To Project Page
    # enter modify mode
    Click Element                            id:edit-project
    Geocontrib Edit Project Description     ${MARKDOWNDESCRIPTION}
    # check that markdown description preview render the titles h1 & h2 on project edit page
    Page Should Contain Element             css:#preview>h1
    Page Should Contain Element             css:#preview>h2
    # submit the form
    Click Button                            id:send-project
    # check that markdown description preview render the titles h1 & h2 on project details page
    Wait Until Page Does Not Contain        Projet en cours de chargement ...
    Page Should Contain Element             css:#preview>h1
    Page Should Contain Element             css:#preview>h2
    # todo: check other pages where a preview is displayed


Create Feature Type - TEST 97
    # Start from main page
    Find Project
    Go To Project Page
    Page Should Not Contain                 ${FEATURETYPENAME}
    Geocontrib Create Featuretype           ${FEATURETYPENAME}        Point
    Geocontrib Add Custom Fields            ${SYMBONAMELIST}    ${SYMBONAMECHAR}    ${SYMBONAMEBOOL}    ${SYMBOPTIONLIST}
    Click Button                            send-feature_type
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    # attendre que le loader disparaissent ! NE MARCHE PAS
    #Wait Until Page Does Not Contain         Récupération des types de signalements en cours... 
    Page Should Contain                     ${FEATURETYPENAME}

Edit Feature Type
    Page Should Contain                     ${FEATURETYPENAME}
    Geocontrib Edit Featuretype             ${FEATURETYPENAME}        ${FEATURETYPEEDITION}
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    Page Should Contain                     ${FEATURETYPEEDITION}

Create Feature - TEST 117
    Page Should Not Contain                 ${FEATURENAME}
    Create Feature                          ${FEATURENAME}       ${FEATURETYPENAME}       ${FEATURETYPEEDITION}     ${X0}   ${Y0}
    # Vérifier que le signalement a été créé
    Page Should Contain                     ${FEATURENAME}
    # Vérifier que le signalement a une description (à améliorer: utilisé une variable)
    Page Should Contain                     Exemple de description

Edit Feature
    # départ depuis la page de détail du signalement juste créé
    # fermer le message d'info si présent pour pouvoir cliquer sur le bouton d'édition
    Discard Info message
    Wait Until Element Is Visible           css:a[href*=editer]
    # check if the feature has been created
    Page Should Contain                     ${FEATURENAME}
    Geocontrib Edit Feature                 ${FEATURENAME}        ${FEATUREEDITION}
    Geocontrib Click Save Changes
    Page Should Contain                     ${FEATUREEDITION}
    # Vérifier que le signalement a le statut 'publié (à améliorer)
    Page Should Contain                     Publié
    # Vérifier que le signalement a une description (à améliorer)
    #Page Should Contain                     ${FEATUREEDITION}

Create Feature Type With Geometry Type Polygone
    # Start from main page
    Find Project
    Go To Project Page
    # Check that the feature type doesn't exist already
    Page Should Not Contain                 ${FEATURETYPENAME}-Polygone
    Geocontrib Create Featuretype           ${FEATURETYPENAME}-Polygone    Polygone
    Geocontrib Add Custom Fields            ${SYMBONAMELIST}    ${SYMBONAMECHAR}    ${SYMBONAMEBOOL}    ${SYMBOPTIONLIST}
    Click Button                            send-feature_type
    # attendre le changement de page
    Wait Until Location Does Not Contain    /type-signalement/ajouter
    Page Should Contain                     ${FEATURETYPENAME}-Polygone

Edit Feature Type Default Symbology
    # Start from main page
    Find Project
    Go To Project Page
    # Go to symbology edition page
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Geocontrib Edit Featuretype Symbology       ${SYMBOLCOLORCODE}   ${SYMBOLOPACITY}   .default
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    # Validate color value
    Element Attribute Value Should Be           css:div.default #couleur         value        ${SYMBOLCOLORCODE}
    # Validate opacity value
    Element Attribute Value Should Be           css:div.default #opacity         value        ${SYMBOLOPACITY}


Edit Custom Field Symbology For List
    # Start from main page
    Find Project
    Go To Project Page
    # Go to symbology edition page
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    # Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMELIST}  ${SYMBOPTIONLIST}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[0]} #couleur         value        ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[0]} #opacity         value        ${SYMBOPTIONOPACITYLIST[0]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[1]} #couleur         value        ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div#${SYMBOPTIONLIST[1]} #opacity         value        ${SYMBOPTIONOPACITYLIST[1]}

Edit Custom Field Symbology For Character Chain
    # Start from main page
    Find Project
    Go To Project Page
    # Go to symbology edition page
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    # Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMECHAR}  ${NONE}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div[id="Vide"] #couleur         value        ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div[id="Vide"] #opacity         value        ${SYMBOPTIONOPACITYLIST[0]}
    # selector with space in ID doesn't work 
    Element Attribute Value Should Be           css:div[id^="Non"] #couleur         value        ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div[id^="Non"] #opacity         value        ${SYMBOPTIONOPACITYLIST[1]}

Edit Custom Field Symbology For Boolean
    # Start from main page
    Find Project
    Go To Project Page
    # Go to symbology edition page
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    # Edit type list
    Geocontrib Edit Custom Field Symbology      ${SYMBOPTIONCOLORLIST}   ${SYMBOPTIONOPACITYLIST}  ${SYMBONAMEBOOL}  ${NONE}
    Click Button                                save-symbology
    # attendre le changement de page
    Wait Until Location Does Not Contain        /symbologie
    Geocontrib Access Featuretype Symbology     ${FEATURETYPENAME}-Polygone
    Wait Until Page Contains                    Couleur
    Element Attribute Value Should Be           css:div[id="Décoché"] #couleur      value       ${SYMBOPTIONCOLORLIST[0]}
    Element Attribute Value Should Be           css:div[id="Décoché"] #opacity      value       ${SYMBOPTIONOPACITYLIST[0]}
    Element Attribute Value Should Be           css:div[id="Coché"] #couleur        value       ${SYMBOPTIONCOLORLIST[1]}
    Element Attribute Value Should Be           css:div[id="Coché"] #opacity        value       ${SYMBOPTIONOPACITYLIST[1]}

Browse Features Filtered
    #Start from main page
    Find Project
    Go To Project Page
    #Create some features to navigate through
    Create Feature      ${FEATURENAME}-2       ${FEATURETYPENAME}       ${FEATURETYPEEDITION}     ${X1}   ${Y1}
    # Start from main page
    Find Project
    Go To Project Page
    Create Feature      ${FEATURENAME}-3       ${FEATURETYPENAME}       ${FEATURETYPEEDITION}     ${X2}   ${Y2}
    # Start from main page
    Find Project
    Go To Project Page
    # go to list and click on first feature containing name
    Geocontrib Browse Feature List         ${FEATURENAME}        ${FEATURETYPENAME}     ${FEATURETYPEEDITION}
    Page Should Contain                    ${FEATURENAME}-3
    Element should have class              css:button[id="previous-feature"]        disabled
    Click Button                           next-feature
    Page Should Contain                    ${FEATURENAME}-2
    Click Button                           next-feature
    Page Should Contain                    ${FEATURENAME}${FEATUREEDITION}
    Element should have class              css:button[id="next-feature"]            disabled

Fast Edit Feature
    #Start from main page
    Find Project
    Go To Project Page
    Geocontrib Activate Fast Edition For Project
    # create a feature type with custom fields
    Page Should Not Contain                 ${FEATURETYPENAME}-FastEdition
    Geocontrib Create Featuretype           ${FEATURETYPENAME}-FastEdition    Point
    Geocontrib Add Custom Fields            ${SYMBONAMELIST}        ${SYMBONAMECHAR}    ${SYMBONAMEBOOL}    ${SYMBOPTIONLIST}
    Click Button                            send-feature_type
    # create a feature
    Create Feature               ${FASTFEATURENAME}      ${FEATURETYPENAME}-FastEdition       ${EMPTY}       ${X3}   ${Y4}
    Discard Info message
    # Edit feature in feature details page
    Geocontrib Fast Edit Feature Detail     ${FASTFEATURENAME}      ${FASTFEATUREDESCRIPTION}       ${FEATURETYPEEDITION}
    Geocontrib Fast Edit Custom Fields      ${SYMBONAMELIST}        ${SYMBONAMECHAR}        ${SYMBOPTIONLIST[0]}
    Click Button                             id:save-fast-edit
    # check fields got values
    Textfield Value Should Be               id:feature_detail_title_input   ${FASTFEATURENAME}${FEATURETYPEEDITION}
    Textarea Value Should Be                name:description                ${FASTFEATUREDESCRIPTION}
    Element Should Contain                  css:#status .default.text > div     Archivé
    Element Should Contain                  css:#${SYMBONAMELIST} .default.text > div     ${SYMBOPTIONLIST[0]}
    Textfield Value Should Be               css:#${SYMBONAMECHAR} input     ${SYMBONAMECHAR}
   Checkbox Should Be Selected             css:#${SYMBONAMEBOOL} input

Import Multi Geometry Feature
    # Start from main page
    Find Project
    Go To Project Page
    # Upload JSON file with multigeomtry feature
    Click Element                               css:.nouveau-type-signalement
    Geocontrib Import Multi Geom File           ${MULTIGEOMFILENAME}
    Click Button                                css:#button-import>button
    Execute JavaScript                          document.getElementById('send-feature_type').scrollIntoView('alignToTop');
    Click Button                                id:send-feature_type
    # Check if feature type has been created
    Wait Until Element Is Not Visible           css:div.ui > div.ui.inverted.dimmer.active
    Element Should Contain                      id:feature_type-list        ${MULTIGEOMFILENAME}
    # Upload features from feature type page
    Click Element                               css:#${MULTIGEOMFILENAME} a.feature-type-title
    Click Element                               id:toggle-show-import
    Geocontrib Import Multi Geom File           ${MULTIGEOMFILENAME}
    Click Element                               id:start-import
    # Wait the import to finish
    Wait Until Page Contains Element            id:table-imports
    Wait Until Page Does Not Contain Element    css:.orange.icon.sync
    # Check if element has been imported successfully
    Page Should Contain Element                 css:#table-imports .green.check.circle.outline.icon

Multiple Feature Edition Of Attributes Within The Same Feature Type
    # Start from main page
    Find Project
    Go To Project Page
    Click Link                                  features-list
    Click Link                                  show-list
    # Select the multiple attributes edition mode
    Click Element                               id:edit-attributes
    # Check if selecting a feature disables checkbox of features from other types
    Click Element                               css:#form-filters #type > .dropdown
    Click Element                               id:${FEATURETYPENAME}${FEATURETYPEEDITION}
    Wait Until Page Does Not Contain            Récupération des signalements en cours...
    # Select all features in this feature type
    ${tableCheckboxes}      Get WebElements     css:#table-features > tbody > tr > td > .checkbox > input
    FOR    ${featureCheckbox}    IN    @{tableCheckboxes}
        Select Checkbox                         ${featureCheckbox}
    END
    # Check if other feature types checkboxes are disabled
    # Close the feature type filter
    Click Element                               css:#form-filters #type > .dropdown > .icon.clear
    Click Element                               css:#form-filters #type > .dropdown
    # Filter with another feature type
    Click Element                               css:#form-filters #type > .dropdown
    Click Element                               id:${MULTIGEOMFILENAME}
    Wait Until Page Does Not Contain            Récupération des signalements en cours...
    # Check the class is disabled
    ${checkboxClass}        Get Element Attribute       css:#table-features > tbody > tr > td > .checkbox       class
    Should Contain          ${checkboxClass}    disabled
    # Edit one attribute of features
    Click Element                               edit-button
    Select Checkbox                             ${SYMBONAMEBOOL}
    Click Button                                save-changes
    # Go back to features list
    Wait Until Page Does Not Contain            Récupération des signalements en cours...
    Discard Info message
    Sleep                                       3s
    Click Link                                  show-list
    # Check that changes had taken effect
    # Filter edited feature type features
    Click Element                               css:#form-filters #type > .dropdown
    Click Element                               id:${FEATURETYPENAME}${FEATURETYPEEDITION}
    # Open first created feature
    Click Link                                  ${FEATURENAME}${FEATUREEDITION}
    Wait Until Page Does Not Contain            Recherche du signalement
    Checkbox Should Be Selected                 ${SYMBONAMEBOOL}

Create Feature Type & Feature with Multiple Choices List CustomField
    # Start from main page
    Find Project
    Go To Project Page
    ## FEATURE TYPE ##
    Page Should Not Contain                     ${MULTICHOICEFEATURETYPENAME}-multiChoices
    Geocontrib Create Featuretype               ${MULTICHOICEFEATURETYPENAME}-multiChoices        Point
    Geocontrib Add MultiChoices CustomField     ${MULTICHOICESLISTNAME}             ${MULTICHOICESLISTOPTIONS}
    Click Button                                send-feature_type
    # attendre le changement de page
    Wait Until Location Does Not Contain        /type-signalement/ajouter
    # attendre que le loader disparaissent ! NE MARCHE PAS
    #Wait Until Page Does Not Contain         Récupération des types de signalements en cours... 
    Page Should Contain                         ${MULTICHOICEFEATURETYPENAME}-multiChoices
    ## FEATURE ##
    Page Should Not Contain                     ${MULTICHOICEFEATURENAME}
    Create Feature                              ${MULTICHOICEFEATURENAME}           ${MULTICHOICEFEATURETYPENAME}       -multiChoices      ${X4}   ${Y4}
    # Vérifier que le signalement a été créé avec les champ personalisés liste à choix multiples
    Wait Until Location Does Not Contain        /signalement/ajouter
    Discard Info message
    FOR    ${choice}    IN    @{MULTICHOICESLISTOPTIONS}
        Element should contain      id:${MULTICHOICESLISTNAME}      ${choice}
    END
    # edit feature
    Click Element                               id:feature_detail_title_input
    Click Element                               css:[data-tooltip="Éditer le signalement"]
    # select some choices
    Wait Until Location contains                /editer
    Select Checkbox                             ${MULTICHOICESLISTOPTIONS[0]}
    Select Checkbox                             ${MULTICHOICESLISTOPTIONS[2]}
    Select Checkbox                             ${MULTICHOICESLISTOPTIONS[4]}
    # save
    Click Button                                id:save-changes
    # check that changes had been written
    Wait Until Location Does Not Contain        /editer
    Checkbox Should Be Selected                 ${MULTICHOICESLISTOPTIONS[0]}
    Checkbox Should Be Selected                 ${MULTICHOICESLISTOPTIONS[2]}
    Checkbox Should Be Selected                 ${MULTICHOICESLISTOPTIONS[4]}


Browse Features At click On Feature Of Project Detail Page
    ## Project page: last features
    # Start from main page
    Find Project
    Go To Project Page
    Click Link                          ${FASTFEATURENAME}${FEATURETYPEEDITION}
    Wait Until Location contains        /signalement-filtre
    Wait Until Page Does Not Contain    Recherche du signalement
    # check that the title in input field correspond to selected feature
    Textfield Should Contain            feature_detail_title_input    ${FASTFEATURENAME}${FEATURETYPEEDITION}
    Element Should Contain              class:fast_browsing           désactivé
    Element Should Contain              class:fast_browsing           par date de création


Edit Project Default Feature Browsing Filter and Sort
    # Start from main page
    Find Project
    Go To Project Page
    Click Element                           id:edit-project
    Wait Until Page Contains                Configuration du parcours de signalement
    # Change values for default filter and sort
    Click Element                           css:#feature_browsing_filter > .dropdown
    Click Element                           id:Type de signalement
    Click Element                           css:#feature_browsing_sort > .dropdown
    Click Element                           id:Date de modification
    Click Button                            id:send-project
    # Check that new values were stored and are retrieved when going back on project edit page
    Click Element                           id:edit-project
    # Check that default filters had been changed since previous test
    Element Text Should Be                  css:#feature_browsing_filter > .dropdown > .default.text > div             Type de signalement
    Element Text Should Be                  css:#feature_browsing_sort > .dropdown > .default.text > div               Date de modification

Browse Features At click On Feature Of Feature Type Detail                    
    # Start from main page
    Find Project
    Go To Project Page
    Click Link                          ${FEATURETYPENAME}${FEATURETYPEEDITION}
    Wait Until Location contains        /type-signalement/
    #Wait Until Page Does Not Contain    Récupération des signalements en cours
    Click Link                          ${FEATURENAME}-3
    # check that the title in input field correspond to selected feature
    Textfield Should Contain            feature_detail_title_input    ${FEATURENAME}-3
    Element Should Contain              css:.fast_browsing > div > div:first-of-type > span            par date de modification
    Element Should Contain              css:.fast_browsing > div > div:last-of-type > span             par type de signalement


Browse Features At click On Feature On Map # To click on a feature might not work, if map or features on map are not the same, it doesn't mean the functionnality doesn't work.
    ## Project page: feature on map
    # Start from main page
    Find Project
    Go To Project Page
    # Geocontrib Click At Coordinates     ${250}         ${235}         ${BROWSER_NAME}         # working with default config in front repository                        3s
    Geocontrib Click At Coordinates     ${346}         ${146}         ${BROWSER_NAME}         # working with config of dev instance
    Wait Until Page Contains Element    id:goToFeatureDetail
    Click Link                          id:goToFeatureDetail
    Wait Until Page Does Not Contain    Recherche du signalement
    # check that the title in input field correspond to selected feature
    Textfield Should Contain            feature_detail_title_input    ${IMPORTED_FEATURE_NAME}
    Wait Until Location contains        /signalement-filtre
    Element Should Contain              css:.fast_browsing > div > div:last-of-type > span             par type de signalement
    Element Should Contain              css:.fast_browsing > div > div:first-of-type > span            par date de modification

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
    Geocontrib Search Project                   ${PROJECTNAME}
    Wait Until Element Is Not Visible           css:div.ui > div.ui.inverted.dimmer.active

Go To Project Page
    Geocontrib Click On Project                 ${PROJECTNAME}
    Wait Until Page Does Not Contain            Projet en cours de chargement ... 

Create Feature
    [Arguments]         ${FEATURENAME}      ${FEATURETYPENAME}      ${FEATURETYPEEDITION}   ${X}    ${Y}
    Geocontrib Create Feature               ${FEATURENAME}          ${FEATURETYPENAME}      ${FEATURETYPEEDITION}
    # switch to drawing on map mode
    Click Element                           css:[title~=Dessiner]
    # set the point is difficult, but putting the point anywhere in canvas works
    Geocontrib Scroll To                    canvas
    Geocontrib Click At Coordinates         ${X}       ${Y}       ${BROWSER_NAME}
    Geocontrib Click Save Changes

Element should have class
    [Arguments]  ${element}  ${className}
    Wait until page contains element  ${element}.${className}

Discard Info message
    TRY
        Click Element                       css:i.close.icon
    EXCEPT    AS    ${err}
        Log    Error occurred: ${err}
    ELSE
        Log    No error occurred!
    END

