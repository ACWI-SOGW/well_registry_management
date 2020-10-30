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

### Changed
-   Modified the Registry model to more closely resemble the editable fields in the Apex Well Registry application. Also added choices to some of the fields to match the Apex well registry.
-   Flag fields are not BooleanFields rather than IntegerFields.
-   Changed the Registry model to MonitoringLocation to better reflect that a registry (the app name) contains monitoring location instances.
-   Set an order for lookups so that pick lists are in alphabetically order
-   Using django-smart-selects to have chaining selects for state and county pick lists.
-   Removed initialization of lookups from migrations and instead added a command to do this. This command will be run following migrations and will update any information that exists. This is also where the agency groups are created.
-   Added a model serializer for UnitsLookup and send both id and description.
-   Line in sand for Django migrations, put all registry table changes into one migration.
-   For USGS users, only allow changes to be made to fields not filled in by NWIS metadata
-   Only allow Bulk Upload and Add Monitoring Location for non USGS users.
-   Populated altitude units, well depth units and local aquifer name when fetching a monitoring location from NWIS.

### Fixed
-   Using whitenoise to serve out the staticfiles when using gunicorn to run the server. Added collectstaticfiles to the Dockerfile.
-   Rather than assigning agency code when saving a monitoring location in the admin, create a custom form which assigns the agency code if the user is a not a superuser.
