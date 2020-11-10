# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

##[Unreleased](https://github.com/ACWI-SOGW/well_registry_management/tree/master)
### Added
-   Added Registry model and admin prototype interface.
-   Added initial registry model with migrations and admin 
-   Added keycloak as the authentication method for the admin.
-   Added lookup models
-   Added filtering of the list of registry to show only sites that are in the user's agency and added permissions to prevent the editing of any other agencies sites.
-   Added labels that match the original well registry app for registry fields
-   Using TextField to display wl_well_purpose_notes, qw_well_purpose_notes, and link fields.
-   Added initial data for lookup fields.
-   Added USWDS and added NGWMN visual identification to all pages.
-   Added validations to fields in monitoring location form
-   Added a fetch_from_nwis view to the admin to allow site meta data to be fetched from NWIS.
-   Added bulk upload view to the admin to allow multiple sites data to be initialized from a csv file.
-   Added the insert_user and update_user to the monitoring location rest endpoint
-   Added pagination to the rest endpoint.
-   Added the ability to download selected monitoring locations.
-   Added ability for non-USGS users to login using the standard Django authentication backend.
-   Added Tootips on all fields 
-   Added Filters for SiteNo (site number) – it could be a partial match, Display flag, National aquifer, state, and county
-   Added Django Admin which allows adding/changing of monitoring locations. This part of the application requires login either through BisonConnect or through a login provided by the well registry administrators.
-   Added a REST API which returns all monitoring locations. The monitoring locations can be filtered by display_flag

### Fixed
-   Fixed the Delete button styling so button is full height.
