# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

## [1.2.0] - 2020-12-17

### Changed
- Redmine 9704: Allow the management of feature links in Django admin
- Redmine 8551: Can import features files with extention "geojson" in addition to "json"
- Redmine 9330: A feature type can be duplicated
- Redmine 9329: Can turn a project into a project template and instatiate a project from a project model
- Django admin improvements
  - Projects list ordered by title
  - FeatureType list ordered by project, title
  - FeatureType list grouped by project
  - Users list ordered by username, last_name, first_name
  - FeatureType geom editable on create (read-only on update)
  - CustomField list ordered by feature_type, label
  - Project creator required (fixing 500 on edit)

### Fixed
- Docker, prevent creating files not readable by nginx
- Redmine 9706: The modification of the basemap form are recorded
- Redmine 9654: Creating a basemap without title doesn't crash
- Redmine 9623: A connected user doesn't see achived features if he is not allowed


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
