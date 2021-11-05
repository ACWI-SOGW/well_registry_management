# Changelog
All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-1.3.0...master)

## [1.3.0](ttps://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-1.2.0...wellregistry-1.3.0) - 2021-11-05
-  Added new agency (PCUWCD)

## [1.2.0](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-1.1.0...wellregistry-1.2.0) - 2021-09-17
### Changed
-   Rename/re-title Well Registry to Monitoring Location Registry

## [1.1.0](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-1.0.0...wellregistry-1.1.0) - 2021-04-29
### Added
-   Added Validation for Decimal values in Bulk Upload. These appear as warnings. 
    
### Changed
-   The well_depth field is now allowed to be blank.


## [1.0.0](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-0.2.0...wellregistry-1.0.0) - 2021-02-02

### Changed
-   Changed the url mapping from registry to apps/location-registry.

## [0.2.0](https://github.com/ACWI-SOGW/well_registry_management/compare/wellregistry-0.1.0...wellregistry-0.2.0) - 2020-12-02

### Added
-   Added tooltips for all monitoring location input fields
-   Added filtering for site_no, state, county, display_flag, and national aquifer 
-   Added Cancel button on edit screens
-   Added tests for /registry/admin/registry/monitoringlocation/add/ and change
-   Added message for bulk upload - Note: A user can only upload a CSV file

### Fixed
-   Fixed the Delete button styling so button is full height.

### Changed 
-   Change text in Well Registry from WL to "water-level" and QW to "water quality"
-   Updated information shown on the monitoring location list

## [0.1.0](https://github.com/ACWI-SOGW/well_registry_management/tree/wellregistry-0.1.0) - 2020-11-05

### Added
-   Added Django Admin which allows adding/changing of monitoring locations. This part of the application requires login either through BisonConnect or through a login provided by the well registry administrators.
-   Added a REST API which returns all monitoring locations. The monitoring locations can be filtered by display_flag


