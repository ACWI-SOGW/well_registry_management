"""
Well Registry project

"""
__version__ = '0.1.0dev'

import csv
import os
from django.conf import settings

INITIAL_DATA_DIR = os.path.join(settings.BASE_DIR, 'registry/management/commands/initial_data/')
nwis_aquifer_lookups=[]
data_src = os.path.join(INITIAL_DATA_DIR, 'lcl_aqfr.csv')
reader = csv.DictReader(open(data_src, 'r'))
for row in reader:
     nwis_aquifer_lookups.append(row)