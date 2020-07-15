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

### Changed
-   Modified the Registry model to more closely resemble the editable fields in the Apex Well Registry application. Also added choices to some of the fields to match the Apex well registry.
-   Flag fields are not BooleanFields rather than IntegerFields.

### Fixed
-   Using whitenoise to serve out the staticfiles when using gunicorn to run the server. Added collectstaticfiles to the Dockerfile.