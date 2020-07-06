"""
Module for Managing lookups used in tests.
"""

from ..models import AgencyLovLookup, AltDatumDimLookup, CountryLookup, CountyLookup, HorzDatumDimLookup
from ..models import NatAqfrLookup, StateLookup, UnitsDimLookup

def create_units_dim(unit_id, unit_desc):
    """Creates a Units Dim lookup data with the specified unit_id and unit_desc. """
    UnitsDimLookup.objects.create(
        unit_id=unit_id,
        unit_desc=unit_desc
    )

def create_lookup_data():
    """Create test lookup data."""
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
    create_units_dim(1, 'Feet')
    create_units_dim(2, 'Centimeters')
