"""
Manage lookup data for tests.
"""

from ..models import AgencyLovLookup, AltDatumDimLookup, CountryLookup, CountyLookup, CountyLookup, HorzDatumDimLookup
from ..models import NatAqfrLookup, StateLookup, UnitsDimLookup, Registry

class LookupData():

    def create():
        AgencyLovLookup.objects.create(
            agency_cd='provider',
            agency_nm='Provider Name'
        )
        AltDatumDimLookup.objects.create(
            adatum_cd='NAVD88',
            adatum_desc='adatum description'
        )
        CountryLookup.objects.create(
            country_cd='US',
            country_nm='United States'
        )
        HorzDatumDimLookup.objects.create(
            hdatum_cd='NAD83',
            hdatum_desc='North American Datum of 1983'
        )
        NatAqfrLookup.objects.create(
            nat_aqfr_cd='N100AKUNCD',
            nat_aqfr_desc='Alaska unconsolidated-deposit aquifers'
        )
        StateLookup.objects.create(
            country_cd= CountryLookup.objects.get(country_cd = 'US'),
            state_cd='CA',
            state_nm='California'
        )
        CountyLookup.objects.create(
            country_cd= CountryLookup.objects.get(country_cd = 'US'),
            state_cd= StateLookup.objects.get(state_cd = 'CA'),
            county_cd='SF',
            county_nm='United States'
        )
        UnitsDimLookup.objects.create(
            unit_id=1,
            unit_desc='Feet'
        )
        UnitsDimLookup.objects.create(
            unit_id=2,
            unit_desc='Centimeters'
        )
