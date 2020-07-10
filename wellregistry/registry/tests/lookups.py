"""
Module for Managing lookups used in tests.
"""

from ..models import AgencyLookup, AltitudeDatumLookup, CountryLookup, CountyLookup, HorizontalDatumLookup
from ..models import NatAqfrLookup, StateLookup, UnitsLookup

def create_lookup_data():
    """Create test lookup data."""
    AgencyLookup.objects.create(
        agency_cd='provider',
        agency_nm='Provider Name'
    )
    AltitudeDatumLookup.objects.create(
        adatum_cd='NAVD88',
        adatum_desc='adatum description'
    )
    CountryLookup.objects.create(
        country_cd='US',
        country_nm='United States'
    )
    HorizontalDatumLookup.objects.create(
        hdatum_cd='NAD83',
        hdatum_desc='North American Datum of 1983'
    )
    NatAqfrLookup.objects.create(
        nat_aqfr_cd='N100AKUNCD',
        nat_aqfr_desc='Alaska unconsolidated-deposit aquifers'
    )
    StateLookup.objects.create(
        country_cd=CountryLookup.objects.get(country_cd='US'),
        state_cd='CA',
        state_nm='California'
    )
    CountyLookup.objects.create(
        country_cd=CountryLookup.objects.get(country_cd='US'),
        state_cd=StateLookup.objects.get(state_cd='CA'),
        county_cd='SF',
        county_nm='United States'
    )
    UnitsLookup.objects.create(
        id=1,
        unit_id=2,
        unit_desc='Feet'
    )
    UnitsLookup.objects.create(
        id=2,
        unit_id=3,
        unit_desc='Centimeters'
    )
