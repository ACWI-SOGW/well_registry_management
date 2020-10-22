"""
Well Registry project

"""
__version__ = '0.1.0dev'

import csv
import os
import pprint
from django.conf import settings

INITIAL_DATA_DIR = os.path.join(settings.BASE_DIR, 'registry/management/commands/initial_data/')
lcl_aqfr_dict=[]
data_src = os.path.join(INITIAL_DATA_DIR, 'lcl_aqfr.csv')
reader = csv.DictReader(open(data_src, 'r'))
for row in reader:
    lcl_aqfr_dict.append(row)