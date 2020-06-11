# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


##[Unreleased](https://github.com/ACWI-SOGW/well_registry_management/tree/master)
### Added
-   Added Registry model and admin prototype interface.
-   Added initial registry model with migrations and admin 
-   Added keycloak as the authentication method for the admin.

### Fixed
-   Using whitenoise to serve out the staticfiles when using gunicorn to run the server. Added collectstaticfiles to the Dockerfile.