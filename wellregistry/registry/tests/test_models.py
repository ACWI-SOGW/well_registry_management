
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import MonitoringLocation, AgencyLookup, CountyLookup, CountryLookup, HorizontalDatumLookup, \
    StateLookup, UnitsLookup, AltitudeDatumLookup, NatAqfrLookup


class TestMonitoringLocationFullClean(TestCase):
    fixtures = ['test_agencies.json', 'test_countries.json', 'test_counties.json',
                'test_states.json', 'test_altitude_datum.json',
                'test_horizontal_datum.json', 'test_nat_aquifer.json', 'test_units.json']

    def setUp(self):
        self.monitoring_location = MonitoringLocation(
            display_flag=False,
            agency=AgencyLookup(agency_cd='USGS'),
            state=StateLookup(pk=39),
            country=CountryLookup(country_cd='US'),
            county=CountyLookup(pk=171),
            site_no='1234567',
            site_name='My test site',
            dec_lat_va=Decimal('98.456'),
            dec_long_va=Decimal('-84.567'),
            horizontal_datum=HorizontalDatumLookup(hdatum_cd='NAD27'),
            alt_va=Decimal('2'),
            altitude_units=UnitsLookup(unit_id=1),
            altitude_datum=AltitudeDatumLookup(adatum_cd='NAD83'),
            nat_aqfr=NatAqfrLookup(nat_aqfr_cd='N100GLCIAL'),
            site_type='WELL',
            aqfr_type='UNCONFINED',
            well_depth=Decimal('4.2'),
            well_depth_units=UnitsLookup(unit_id=1),
            wl_sn_flag=False,
            wl_baseline_flag=False,
            qw_sn_flag=False,
            qw_baseline_flag=False,
            wl_well_chars='',
            qw_well_chars=''
        )

    def test_valid_when_display_flag_false(self):
        try:
            self.monitoring_location.full_clean()
        except ValidationError as errors:
            self.fail(f'monitoring_location should be valid. Found {errors.message_dict}')

    def test_invalid_when_site_no_blank(self):
        self.monitoring_location.site_no = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.site_no = '         '
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_site_name_blank(self):
        self.monitoring_location.site_name = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.site_name = '         '
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_state_blank(self):
        self.monitoring_location.state = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_county_blank(self):
        self.monitoring_location.county = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_latitude_blank(self):
        self.monitoring_location.dec_lat_va = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_longitude_blank(self):
        self.monitoring_location.dec_long_va = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_horizontal_datum_blank(self):
        self.monitoring_location.horizontal_datum = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_altitude_blank(self):
        self.monitoring_location.alt_va = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_altitude_units_blank(self):
        self.monitoring_location.altitude_units = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_national_aquifer_blank(self):
        self.monitoring_location.nat_aqfr = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_altitude_datum_blank(self):
        self.monitoring_location.altitude_datum = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_site_type_blank(self):
        self.monitoring_location.site_type = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_valid_when_display_flag_true_sn_flags_false(self):
        self.monitoring_location.display_flag = True
        try:
            self.monitoring_location.full_clean()
        except ValidationError as errors:
            self.fail(f'monitoring_location should be valid. Found {errors.message_dict}')

    def test_invalid_when_site_type_well_and_aquifer_type_blank(self):
        self.monitoring_location.site_type = 'WELL'
        self.monitoring_location.aqfr_type = ''
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_depth_unit_blank(self):
        self.monitoring_location.well_depth = '5'
        self.monitoring_location.well_depth_units = None
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_depth_unit_not_blank(self):
        self.monitoring_location.well_depth = ''
        self.monitoring_location.well_depth_units = UnitsLookup(unit_id=1)
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_valid_when_display_flag_true_and_wl_sn_flags_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.wl_sn_flag = True
        self.monitoring_location.wl_well_purpose = 'Other'
        self.monitoring_location.wl_well_type = 'Trend'
        try:
            self.monitoring_location.full_clean()
        except ValidationError as errors:
            self.fail(f'monitoring_location should be valid. Found {errors.message_dict}')

    def test_invalid_when_display_flag_true_and_wl_sn_flag_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.wl_sn_flag = True
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.wl_well_type = 'Trend'
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.wl_well_type = ''
        self.monitoring_location.wl_well_purpose = 'Other'

        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_display_flag_true_and_wl_sn_flag_true_and_wl_baseline_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.wl_sn_flag = True
        self.monitoring_location.wl_well_purpose = 'Other'
        self.monitoring_location.wl_well_type = 'Trend'
        self.monitoring_location.wl_baseline_flag = True
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_valid_when_display_flag_true_and_qw_sn_flags_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.qw_sn_flag = True
        self.monitoring_location.qw_well_purpose = 'Other'
        self.monitoring_location.qw_well_type = 'Trend'
        try:
            self.monitoring_location.full_clean()
        except ValidationError as errors:
            self.fail(f'monitoring_location should be valid. Found {errors.message_dict}')

    def test_invalid_when_display_flag_true_and_qw_sn_flag_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.qw_sn_flag = True
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.qw_well_type = 'Trend'
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

        self.monitoring_location.qw_well_type = ''
        self.monitoring_location.qw_well_purpose = 'Other'

        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()

    def test_invalid_when_display_flag_true_and_qw_sn_flag_true_and_qw_baseline_true(self):
        self.monitoring_location.display_flag = True
        self.monitoring_location.qw_sn_flag = True
        self.monitoring_location.qw_well_purpose = 'Other'
        self.monitoring_location.qw_well_type = 'Trend'
        self.monitoring_location.qw_baseline_flag = True
        with self.assertRaises(ValidationError):
            self.monitoring_location.full_clean()
