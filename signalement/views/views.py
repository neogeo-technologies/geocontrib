from django.shortcuts import render
import datetime

dummy_projects = {
    "l49": {
        "id": "l49",
        "title": "L49",
        "description": "Publication de la localisation de travaux planifiés sur la voie publique en vue de "
                       "l'application de l'article L49 du Code des postes et des communications électroniques.",
        "illustration": "http://www.montpellier3m.fr/sites/default/files/vignettes/actualite/travaux_2.jpg",
        "min_access_level_for_published_issues": "anonymous",
        "date_creation": datetime.date(2014, 8, 24),
        "is_moderated": False,
        "nb_of_contributors": 13,
        "nb_of_issues": 134,
        "nb_of_comments": 3,
    },
    "adresses": {
        "id": "adresses",
        "title": "Adresses",
        "description": "Identification des erreurs ou absences dans les bases d'adresse de référence. Les signalements "
                       "recueillis concernent aussi bien les erreurs de localisation, de numérotation et de "
                       "dénomination.",
        "illustration": "https://www.rapid-sign.com/ori-numeros-de-maison-noir-13cm-74.jpg",
        "min_access_level_for_published_issues": "connected",
        "date_creation": datetime.date(2012, 4, 12),
        "is_moderated": False,
        "nb_of_contributors": 32,
        "nb_of_issues": 152,
        "nb_of_comments": 223,
    },
    "ortho-2018": {
        "id": "ortho-2018",
        "title": "Ortho 2018",
        "description": "Identification des non-conformités de l'ortho 2018 par rapport à ses spécifications&nbsp;: "
                       "précision planimétrique, radiométrie, colorimétrie...",
        "illustration": "https://www.geopicardie.fr/geoserver/geopicardie/ows?SERVICE=WMS&LAYERS=picardie_ortho_ign_2013_vis&TRANSPARENT=true&VERSION=1.3.0&FORMAT=image%2Fpng&EXCEPTIONS=XML&REQUEST=GetMap&STYLES=&SLD_VERSION=1.1.0&CRS=EPSG%3A3857&BBOX=276314.73430822,6307626.8969942,276950.11710584,6308262.2797919&WIDTH=532&HEIGHT=532",
        "min_access_level_for_published_issues": "contributor",
        "date_creation": datetime.date(2018, 9, 23),
        "is_moderated": False,
        "nb_of_contributors": 5,
        "nb_of_issues": 28,
        "nb_of_comments": 41,
    },
    "occupation-du-sol-2d": {
        "id": "occupation-du-sol-2d",
        "title": "Occupation du sol 2D",
        "description": "Identification des anomalies présentes dans la base de l'occupation du sol 2D issues d'erreur "
                       "flagrantes de photo-interprétation.",
        "illustration": "https://www.geopicardie.fr/geoserver/geopicardie/ows?SERVICE=WMS&LAYERS=mos_picardie&EXCEPTIONS=XML&FORMAT=image%2Fpng&TRANSPARENT=TRUE&VERSION=1.3.0&SLD_VERSION=1.1.0&REQUEST=GetMap&STYLES=&CRS=EPSG%3A3857&BBOX=284696.53219112,6305613.2590304,294862.65695304,6315779.3837923&WIDTH=532&HEIGHT=532",
        "min_access_level_for_published_issues": "contributor",
        "date_creation": datetime.date(2018, 5, 4),
        "is_moderated": False,
        "nb_of_contributors": 12,
        "nb_of_issues": 41,
        "nb_of_comments": 109,
    },
    "decheteries": {
        "id": "decheteries",
        "title": "Déchèteries",
        "description": "Lacolisation des déchèteries en Région Hauts-de-France.",
        "illustration": "https://image.freepik.com/photos-gratuite/closeup-mains-separer-bouteilles-plastique_53876-46918.jpg",
        "min_access_level_for_published_issues": "anonymous",
        "date_creation": datetime.date(2018, 5, 4),
        "is_moderated": True,
        "nb_of_contributors": 20,
        "nb_of_issues": 131,
        "nb_of_comments": 12,
    },
}


def index(request):
    context = {
        "title": "Collab",
        "projects": dummy_projects,
    }
    return render(request, 'signalement/index.html', context)


def my_account(request):
    context = {"title": "My account"}
    return render(request, 'signalement/my_account.html', context)


def legal(request):
    context = {"title": "Mentions légales"}
    return render(request, 'signalement/legal.html', context)


def site_help(request):
    context = {"title": "Aide"}
    return render(request, 'signalement/help.html', context)


def project(request, project_slug):

    # Get project info from slug
    project_info = dummy_projects.get(project_slug)

    context = {
        "title": project_info.get("title") if project_info else "Nom du projet",
        "project": project_info,
    }
    return render(request, 'signalement/project_home.html', context)


def project_users(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : users".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)


def project_issues_list(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : issues list".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)


def project_issues_map(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : issues map".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)


def project_issue_detail(request, project_slug, issue_id):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : issue detail {}".format(project_slug, issue_id),
    }
    return render(request, 'signalement/empty.html', context)


def project_import_issues(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : import issues".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)


def project_import_geo_image(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : import geo image".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)


def project_download_issues(request, project_slug):
    # Get project info from slug
    context = {
        "title": "Nom du projet",
        "content": "{} project : download issues".format(project_slug),
    }
    return render(request, 'signalement/empty.html', context)
