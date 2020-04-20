# Well Registry Management System

[![Build Status](https://travis-ci.org/ACWI-SOGW/well_registry_management.svg?branch=master)](https://travis-ci.org/ACWI-SOGW/well_registry_management)
[![codecov](https://codecov.io/gh/ACWI-SOGW/well_registry_management/branch/master/graph/badge.svg)](https://codecov.io/gh/ACWI-SOGW/well_registry_management)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6af41d5963ee48c1bb9f8a83ea338b46)](https://www.codacy.com/gh/ACWI-SOGW/well_registry_management?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ACWI-SOGW/well_registry_management&amp;utm_campaign=Badge_Grade)


Application for management of groundwater monitoring locations.

## Local Environment Setup
A local development environment can be setup by running:

```bash
make env
```

## Development Server
To run the development server, create a `local_settings.py` file as a sibling of `settings.py`. Add a `SECRET_KEY` value
with some random stuff (e.g `SECRET_KEY = 'sjfio3u903RaggleFraggle'`).

The Django local development can be run via:

```bash
make watch
```


