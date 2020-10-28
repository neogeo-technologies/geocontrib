# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## Unreleased

## [1.1.1] - 2020-10-29

### Changed
- increase thickness of segments of features and reduced the transparency of dotted features

### Fixed
- Display creator in feature and feature type
- Responsive issue when the layer is very long in the basemap form
- Add title in project, feature type and feature
- Access to the project when no project rank defined
- Some pages where missing the title in the browser tabs
- The features are now filtered when search on the map
- The search in the list of features now stay in the same page
- The Georchestra plugin now keeps user rights defined in GeoContrib
- Draft features are now hidden on the section "Last features"
- Empty comments are now blocked

## [1.1.0] - 2020-08-28

### Changed
- increase thickness of segments borders in the basemap project management form

### Fixed
- update addok geocoder provider url in leaflet-control-geocoder to fix a mixed content error on client side
- doest not reload flatpages.json if flatpages records exist in database
- fix incoherent ending h3 tags in flatpages.json

## [1.1.0-rc1] - 2020-08-19
### Added
- geOrchestra plugin: automatically associate role to users when the user database is synchronised (see
[geOrchestra plugin](plugin_georchestra/README.md))
- add a function to search for places and addresses in the interactive maps. This new feature comes with new settings:
`GEOCODER_PROVIDERS` and `SELECTED_GEOCODER`
- add a button to for feature creation in a feature detail page
- add a function in the Django admin page of the feature type for creating a SQL view
- add a `FAVICON_PATH` setting. Default favicon is the Neogeo Technologies logo

### Changed
- enable edition of a feature type if there is not yet any feature associated with it
- sort users list by last_name, first_name and then username
- change the label of the feature type field `title` in the front-end form (Titre -> Nom)
- change the data model for basemaps: one basemap may contain several layers. Layers are declared by GéoContrib
admin users. Basemaps are created by project admin users by selecting layers, ordering them and setting the opacity
of each of them. End users may switch from one basemap to another in the interactive maps. One user can change
the order of the layers and their opacity in the interactive maps. These personnal adjustments are stored in the
web browser of the user (local storage) and do not alter the basemaps as seen by other users.
- change default value for `LOGO_PATH` setting: Neogeo Technologie logo. This new image is located in the media
directory.
- change all visible names in front-end and docs from `Geocontrib` to `GéoContrib`
- set the leaflet background container to white
- increase the width of themap in feature_list.html

### Fixed
- fix tests on exif tag extraction
- fix serialisation of field archieved_on of features
- use https instead of http on link to sortable.js
- fix typos: basemaps management error message
- fix visibility of draft features

### Security
- upgrade Pillow from 6.2.2 to 7.2.0 (Python module used for exif tags extraction)
