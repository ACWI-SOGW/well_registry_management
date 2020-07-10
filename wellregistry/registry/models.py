"""
Well Registry ORM object.
"""

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class AgencyLookup(models.Model):
    """Model definition for the agency table, lookup only"""
    agency_cd = models.CharField(max_length=50, unique=True)
    agency_nm = models.CharField(max_length=150, blank=True, null=True)
    agency_med = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'agency'

    def __str__(self):
        return self.agency_nm


class AltitudeDatumLookup(models.Model):
    """Model definition for the altitude_datum table, lookup only"""
    adatum_cd = models.CharField(max_length=10, unique=True)
    adatum_desc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'altitude_datum'

    def __str__(self):
        return self.adatum_desc


class CountryLookup(models.Model):
    """Model definition for the country table, lookup only"""
    country_cd = models.CharField(unique=True, max_length=2)
    country_nm = models.CharField(max_length=48)

    class Meta:
        db_table = 'country'

    def __str__(self):
        return self.country_nm

class CountyLookup(models.Model):
    """Model definition for the county table, lookup only"""
    country_cd = models.ForeignKey('CountryLookup', models.DO_NOTHING, db_column='country_cd')
    state_cd = models.ForeignKey('StateLookup', models.DO_NOTHING, db_column='state_cd')
    county_cd = models.CharField(max_length=3)
    county_nm = models.CharField(max_length=48)

    class Meta:
        db_table = 'county'
        unique_together = (('country_cd', 'state_cd', 'county_cd'),)

    def __str__(self):
        return self.county_nm

class HorizontalDatumLookup(models.Model):
    """Model definition for the horizontal_datum table, lookup only"""
    hdatum_cd = models.CharField(max_length=10, unique=True)
    hdatum_desc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'horizontal_datum'

    def __str__(self):
        return self.hdatum_desc


class NatAqfrLookup(models.Model):
    """Model definition for the nat_aqfr table, lookup only"""
    nat_aqfr_cd = models.CharField(unique=True, max_length=10)
    nat_aqfr_desc = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'nat_aqfr'

    def __str__(self):
        return self.nat_aqfr_desc


class StateLookup(models.Model):
    """Model definition for the state table, lookup only"""
    country_cd = models.ForeignKey('CountryLookup', on_delete=models.DO_NOTHING, db_column='country_cd')
    state_cd = models.CharField(max_length=2)
    state_nm = models.CharField(max_length=53)

    class Meta:
        db_table = 'state'
        unique_together = (('country_cd', 'state_cd'),)

    def __str__(self):
        return self.state_nm


class UnitsLookup(models.Model):
    """Model definition for the units_dim table, lookup only"""
    unit_id = models.IntegerField(unique=True, default=-1)
    unit_desc = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'units'

    def __str__(self):
        return self.unit_desc

WELL_TYPES = [('1', 'Surveillance'), ('2', 'Trend'), ('3', 'Special')]
WELL_CHARACTERISTICS = [('1', 'Background'),('2', 'Suspected/Anticipated Changes'), ('3', 'Known Changes')]
WELL_PURPOSES = [('1', 'Dedicated Monitoring/Observation'), ('2', 'Other')]

class Registry(models.Model):
    """
    Django Registry Model.

    # python manage.py makemigrations and migrate
    """
    site_no = models.CharField(max_length=16)
    site_name = models.CharField(max_length=300, blank=True)
    agency = models.ForeignKey(AgencyLookup, on_delete=models.PROTECT, db_column='agency_cd', null=True,
                               to_field='agency_cd')

    country = models.ForeignKey(CountryLookup, on_delete=models.PROTECT, db_column='country_cd',
                                null=True, blank=True, to_field='country_cd')
    state = models.ForeignKey(StateLookup, on_delete=models.PROTECT, db_column='state_id', null=True, blank=True)
    county = models.ForeignKey(CountyLookup, on_delete=models.PROTECT,
                               db_column='county_id', null=True, blank=True)

    dec_lat_va = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    dec_long_va = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    horizontal_datum = models.ForeignKey(HorizontalDatumLookup, on_delete=models.PROTECT,
                                         db_column='horizontal_datum_cd', null=True, blank=True,
                                         to_field='hdatum_cd')
    horz_method = models.CharField(max_length=300, blank=True)
    horz_acy = models.CharField(max_length=300, blank=True)

    alt_va = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    altitude_datum = models.ForeignKey(AltitudeDatumLookup, on_delete=models.PROTECT,
                                       db_column='altitude_datum_cd', null=True, blank=True,
                                       to_field='adatum_cd')
    altitude_units = models.ForeignKey(UnitsLookup, on_delete=models.PROTECT, db_column='altitude_units',
                                       to_field='unit_id', null=True, blank=True)
    alt_method = models.CharField(max_length=300, blank=True)
    alt_acy = models.CharField(max_length=300, blank=True)

    well_depth = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    well_depth_units = models.ForeignKey(UnitsLookup, related_name='+', db_column='well_depth_units',
                                         on_delete=models.PROTECT, to_field='unit_id', null=True, blank=True)

    nat_aqfr = models.ForeignKey(NatAqfrLookup, on_delete=models.PROTECT,
                                 db_column='nat_aqfr_cd', to_field='nat_aqfr_cd', null=True, blank=True)
    local_aquifer_name = models.CharField(max_length=100, blank=True)

    site_type = models.CharField(max_length=10, blank=True, choices=[('WELL', 'Well'), ('SPRING', 'Spring')])
    aqfr_type = models.CharField(max_length=10, blank=True, db_column='aqfr_char',
                                 choices=[('CONFINED', 'Confined'), ('UNCONFINED', 'Unconfined')])

    wl_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_network_name = models.CharField(max_length=50, blank=True, db_column='wl_sys_name')
    wl_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_well_type = models.CharField(max_length=3, blank=True, choices=WELL_TYPES)
    wl_well_chars = models.CharField(max_length=3, blank=True, choices=WELL_CHARACTERISTICS)
    wl_well_purpose = models.CharField(max_length=15, blank=True, choices=WELL_PURPOSES)
    wl_well_purpose_notes = models.CharField(max_length=4000, blank=True)

    qw_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_network_name = models.CharField(max_length=50, blank=True, db_column='qw_sys_name')
    qw_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_well_type = models.CharField(max_length=3, blank=True, choices=WELL_TYPES)
    qw_well_chars = models.CharField(max_length=3, blank=True, choices=WELL_CHARACTERISTICS)
    qw_well_purpose = models.CharField(max_length=15, blank=True, choices=WELL_PURPOSES)
    qw_well_purpose_notes = models.CharField(max_length=4000, blank=True)

    link = models.CharField(max_length=500, blank=True)

    display_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])

    insert_user = models.ForeignKey(User, null=True, on_delete=models.PROTECT, editable=False, related_name='+')
    update_user = models.ForeignKey(User, null=True, on_delete=models.PROTECT, editable=False, related_name='+')

    insert_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        unique_together = (('site_no', 'agency'),)

    def __str__(self):
        """Default string."""
        str_rep = f'{self.agency}:{self.site_no}'
        return str_rep
