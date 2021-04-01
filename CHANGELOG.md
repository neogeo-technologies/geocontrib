# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

### Fixed
- Redmin 10338 : can create a feature type that has no list of values custom field and colors associated to it
- Security issues with Pillow and DRF

## [1.3.2] - 2021-02-23

### Changed
- Redmine 10053 : Can change color of a feature against its custom field value
- Redmine 10054 + 10266 : Can query properties of basemaps
- Added a scale on the maps

### Fixed
- Renamed Collab to Geocontrib in some mails

## [1.3.0 - 1.3.1] - 2021-02-23
Never released

## [1.2.3] - 2021-02-11

### Fixed
- Redmine 10209 fixed basemaps can't be saved
- Redmine 10228 added project menu on feature details
- Redmine 9962 highlight django errors

## [1.2.2] - 2021-02-11

Never released

## [1.2.1] - 2021-02-04

### Changed
- Redmine 9754 Docker can overide login URL

### Fixed
- Docker, give default values for email configuration
- Redmine 9834 use LDAP pagination
- Redmine 9839 improve feature import time
- Redmine 9846 FeatureLink cleanup
- Redmine 9848 fix admin FeatureLink filters
- Redmine 9905 can't give an empty basemap title
- Redmine 9926 fix impossible to create 2 features
- Redmine 9929 fix maps icons missing
- Redmine 9985 fix PostgreSQL view creation of a feature when adding/removing custom fields
- Redmine 9986 fix PostgreSQL view creation when no status selected
- Redmine 10083 fix a empty feature link removes the geometry of a feature on save
- Redmine 10105 fix project types don't copy feature types
- Redmine 10142 improve performance when a feature type has many features


## [1.2.0] - 2020-12-17

This evolution need a migration (manage.py migrate)

### Changed
- Redmine 9704: Allow the management of feature links in Django admin
- Redmine 8551: Can import features files with extention "geojson" in addition to "json"
- Redmine 9330: A feature type can be duplicated
- Redmine 9329: Can turn a project into a project template and instantiate a project from a project model
- Redmine 9544: Addition of Sortable JS library
- Redmine 9507: Added help on authorized characters
- Redmine 9331: Imports with identical geometry are considered to be duplicates
- Django admin improvements
  - Projects list ordered by title
  - FeatureType list ordered by project, title
  - FeatureType list grouped by project
  - Users list ordered by username, last_name, first_name
  - FeatureType geom editable on create (read-only on update)
  - CustomField list ordered by feature_type, label
  - Project creator required (fixing 500 on edit)
  - Added help on authorized characters when user create a view PostgreSQL

### Fixed
- Docker, prevent creating files not readable by nginx
- Redmine 9706: The modification of the basemap form are recorded
- Redmine 9654: Creating a basemap without title doesn't crash
- Redmine 9623: A connected user doesn't see achived features if he is not allowed
- Redmine 9745: Geolocalised images are visible
- Redmine 9619 : Fix bug for project creation from Django
- Redmine 9490: Fix bug when a custom field is duplicated
- Redmine 9527: Show "0" instead of « None » in the project settings
- Redmine 9526: Fix bug for view creation from Django
- Redmine 9498: Display the login if the user does not have a first and last name
- Redmine 9402: Return to the project page after modifying the project
- Redmine 9401: Error message if the archiving time is greater than the deletion time

## [1.1.3] - 2020-11-13

### Changed
- Docker image can handle forms with 10000 parameters (or more via the `DATA_UPLOAD_MAX_NUMBER_FIELDS` environement variable).
  This allows to handle more than 500 users in the projet

## [1.1.2] - 2020-10-30

### Fixed
- The custom basemaps appears correctly in the list of features

## [1.1.1] - 2020-10-29

### Changed
- Increases thickness of segments of features and reduces transparency of dotted features

### Fixed
- The creator is correctly displayed in the features and the feature types
- In the basemaps form, the display of a very long layer name is now responsive
- A browser title (tab) is now displayed for all pages
- Projects with limited access are no longer accessible to everyone
- The features are now filtered when search on the map
- The search in the list of features now stays in the same page
- The Georchestra plugin now keeps user rights defined in GeoContrib
- Draft features are now hidden on the section "Last features"
- Empty comments are now blocked

## [1.1.0] - 2020-08-28

### Changed
- Increases thickness of segments borders in the basemap project management form

### Fixed
- Updates addok geocoder provider url in leaflet-control-geocoder to fix a mixed content error on client side
- flatpages.json does not reload if flatpages records exist in database
- Fixes incoherent ending h3 tags in flatpages.json

## [1.1.0-rc1] - 2020-08-19
### Added
- GeOrchestra plugin automatically associates role to users when the user database is synchronised (see
[geOrchestra plugin](plugin_georchestra/README.md))
- Adds a function to search for places and addresses in the interactive maps. This new feature comes with new settings:
`GEOCODER_PROVIDERS` and `SELECTED_GEOCODER`
- Adds a button to search for feature creation in a feature detail page
- Adds a function in the Django admin page of the feature type for creating a SQL view
- Adds a `FAVICON_PATH` setting. Default favicon is the Neogeo Technologies logo

### Changed
- Enables edition of a feature type if there is no feature associated with it yet
- Sorts users list by last_name, first_name and then username
- Changes the label of the feature type field `title` in the front-end form (Titre -> Nom)
- Changes the data model for basemaps: one basemap may contain several layers. Layers are declared by GéoContrib
admin users. Basemaps are created by project admin users by selecting layers, ordering them and setting the opacity
of each of them. End users may switch from one basemap to another in the interactive maps. One user can change
the order of the layers and their opacity in the interactive maps. These personnal adjustments are stored in the
web browser of the user (local storage) and do not alter the basemaps as seen by other users.
- Changes default value for `LOGO_PATH` setting: Neogeo Technologie logo. This new image is located in the media
directory.
- Changes all visible names in front-end and docs from `Geocontrib` to `GéoContrib`
- Sets the leaflet background container to white
- Increases the width of themap in feature_list.html

### Fixed
- Fixes tests on exif tag extraction
- Fixes serialisation of field archieved_on of features
- Uses https instead of http on link to sortable.js
- Fixes typos: basemaps management error message
- Fixes visibility of draft features

### Security
- Upgrades Pillow from 6.2.2 to 7.2.0 (Python module used for exif tags extraction)
