"""
Initializes the registry application
"""
import csv
import os
from django.conf import settings

def _get_nwis_aquifer_lookups():
    lookups = []
    data_src = os.path.join(settings.BASE_DIR, 'registry/management/commands/initial_data', 'lcl_aqfr.csv')
    reader = csv.DictReader(open(data_src, 'r'))
    for row in reader:
        lookups.append(row)

    return lookups


nwis_aquifer_lookups = _get_nwis_aquifer_lookups()
