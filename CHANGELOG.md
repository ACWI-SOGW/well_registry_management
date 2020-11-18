# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-0.1.0...master)
### Added
-   Added Tooltips for all monitoring location input fields
-   Added Filtering for site_no, state, county, dislplay_flag, and national aquifer 
-   Added Cancel button on edit screens
-   Added message for bulk upload - Note: A user can only upload a CSV file
### Fixed
-   Fixed the Delete button styling so button is full height.
### Changed 
-   Change text in Well Registry from WL to "water-level" and QW to "water quality"
-   Updated information shown on the monitoring locations list
## [0.1.0](https://github.com/ACWI-SOGW/well_registry_management/tree/wellregistry-0.1.0) - 2020-11-05
### Added
-   Added Django Admin which allows adding/changing of monitoring locations. This part of the application requires login either through BisonConnect or through a login provided by the well registry administrators.
-   Added a REST API which returns all monitoring locations. The monitoring locations can be filtered by display_flag


