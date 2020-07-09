"""
Well Registry ORM object.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    nat_aqfr_desc = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        db_table = 'nat_aqfr'

    def __str__(self):
        return self.nat_aqfr_desc


class StateLookup(models.Model):
    """Model definition for the state table, lookup only"""
    country_cd = models.ForeignKey('CountryLookup', models.DO_NOTHING, db_column='country_cd')
    state_cd = models.CharField(max_length=2)
    state_nm = models.CharField(max_length=53)

    class Meta:
        db_table = 'state'
        unique_together = (('country_cd', 'state_cd'),)

    def __str__(self):
        return self.state_nm


class UnitsLookup(models.Model):
    """Model definition for the units_dim table, lookup only"""
    unit_desc = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'units'

    def __str__(self):
        return self.unit_desc

class Registry(models.Model):
    """
    Django Registry Model.

    # python manage.py makemigrations and migrate
    """
    # these columns use foreign keys
    agency = models.ForeignKey(AgencyLookup, on_delete=models.PROTECT, db_column='agency_cd', null=True,
                               to_field='agency_cd') # AGENCY.AGENCY_CD
    well_depth_units = models.ForeignKey(UnitsLookup, related_name='+', db_column='well_depth_units',
                                         on_delete=models.PROTECT, null=True) # UNIT.ID
    altitude_datum = models.ForeignKey(AltitudeDatumLookup, on_delete=models.PROTECT,
                                       db_column='altitude_datum_cd', default=0, null=True,
                                       to_field='adatum_cd') # ALTITUDE_DATUM.ADATUM_CD
    altitude_units = models.ForeignKey(UnitsLookup, on_delete=models.PROTECT, db_column='altitude_units',
                                       null=True) # UNIT.UNIT_ID
    horizontal_datum = models.ForeignKey(HorizontalDatumLookup, on_delete=models.PROTECT,
                                         db_column='horizontal_datum_cd', null=True,
                                         to_field='hdatum_cd') # HORZONITAL_DATUM.HDATUM_CD
    nat_aqfr = models.ForeignKey(NatAqfrLookup, on_delete=models.PROTECT,
                                 db_column='nat_aqfr_cd', to_field='nat_aqfr_cd', null=True) # NAT_AQFR.NAT_AQFR_CD
    country = models.ForeignKey(CountryLookup, on_delete=models.PROTECT, db_column='country_cd',
                                null=True, to_field='country_cd')  # COUNTRY.COUNTRY_CD
    state = models.ForeignKey(StateLookup, on_delete=models.PROTECT, db_column='state_id', null=True) # STATE.ID
    county = models.ForeignKey(CountyLookup, on_delete=models.PROTECT,
                               db_column='county_id', null=True) # COUNTY.ID

    agency_nm = models.CharField(max_length=200, blank=True)
    agency_med = models.CharField(max_length=200, blank=True)
    site_no = models.CharField(max_length=16)
    site_name = models.CharField(max_length=300, blank=True)
    dec_lat_va = models.DecimalField(max_digits=11, decimal_places=8)
    dec_long_va = models.DecimalField(max_digits=11, decimal_places=8)
    alt_va = models.DecimalField(max_digits=10, decimal_places=6)
    nat_aqfr_desc = models.CharField(max_length=100, blank=True)
    local_aquifer_name = models.CharField(max_length=100, blank=True)
    # for all flags ensure null->0 on load
    qw_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_well_chars = models.CharField(max_length=3, blank=True)
    qw_well_purpose = models.CharField(max_length=15, blank=True)
    wl_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    # for some reason this field has a couple with 999 but there is no cache use case and not a lookup field
    wl_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_well_chars = models.CharField(max_length=3, blank=True)
    wl_well_purpose = models.CharField(max_length=15, blank=True)
    data_provider = models.CharField(max_length=30, blank=True)
    qw_sys_name = models.CharField(max_length=50, blank=True)
    wl_sys_name = models.CharField(max_length=50, blank=True)
    pk_siteid = models.CharField(max_length=37, blank=True)
    display_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_data_provider = models.CharField(max_length=20, blank=True)
    qw_data_provider = models.CharField(max_length=20, blank=True)
    lith_data_provider = models.CharField(max_length=20, blank=True)
    const_data_provider = models.CharField(max_length=20, blank=True)
    well_depth = models.DecimalField(max_digits=11, decimal_places=8,)
    link = models.CharField(max_length=500, blank=True)
    wl_well_purpose_notes = models.CharField(max_length=4000, blank=True)
    qw_well_purpose_notes = models.CharField(max_length=4000, blank=True)
    insert_user_id = models.CharField(max_length=50, blank=True)
    update_user_id = models.CharField(max_length=50, blank=True)
    wl_well_type = models.CharField(max_length=3, blank=True)
    qw_well_type = models.CharField(max_length=3, blank=True)
    local_aquifer_cd = models.CharField(max_length=20, blank=True)
    review_flag = models.CharField(max_length=1, blank=True)
    site_type = models.CharField(max_length=10, blank=True)
    aqfr_char = models.CharField(max_length=10, blank=True)
    horz_method = models.CharField(max_length=300, blank=True)
    horz_acy = models.CharField(max_length=300, blank=True)
    alt_method = models.CharField(max_length=300, blank=True)
    alt_acy = models.CharField(max_length=300, blank=True)

    insert_date = models.DateTimeField(auto_now_add=True, editable=False)
    update_date = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        """Default string."""
        str_rep = f'{self.agency.agency_cd}:{self.site_no}'
        return str_rep
