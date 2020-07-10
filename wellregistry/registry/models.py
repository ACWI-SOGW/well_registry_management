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
    country_cd = models.ForeignKey('CountryLookup', on_delete=models.PROTECT, db_column='country_cd',
                                   to_field='country_cd')
    state_id = models.ForeignKey('StateLookup', on_delete=models.PROTECT, db_column='state_id')
    county_cd = models.CharField(max_length=3)
    county_nm = models.CharField(max_length=48)

    class Meta:
        db_table = 'county'
        unique_together = (('country_cd', 'state_id', 'county_cd'),)

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
    country_cd = models.ForeignKey('CountryLookup', on_delete=models.PROTECT, db_column='country_cd',
                                   to_field='country_cd')
    state_cd = models.CharField(max_length=2)
    state_nm = models.CharField(max_length=53)

    class Meta:
        db_table = 'state'
        unique_together = (('country_cd', 'state_cd'),)

    def __str__(self):
        return self.state_nm


class UnitsLookup(models.Model):
    """Model definition for the units_dim table, lookup only"""
    unit_id = models.IntegerField(unique=True)
    unit_desc = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'units'

    def __str__(self):
        return self.unit_desc

class Registry(models.Model):
    """
    Django Registry Model.

    # python manage.py makemigrations and migrate
    These fields names are nasty but they are to match the original.
    We could refactor later.

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

    agency_nm = models.CharField(max_length=200)
    agency_med = models.CharField(max_length=200)
    site_no = models.CharField(max_length=16)
    site_name = models.CharField(max_length=300)
    # have to keep an eye on these when in postgres. in sqlite3 they loose the given precision
    dec_lat_va = models.DecimalField(max_digits=11, decimal_places=8)
    dec_long_va = models.DecimalField(max_digits=11, decimal_places=8)
    alt_va = models.DecimalField(max_digits=10, decimal_places=6)
    nat_aqfr_desc = models.CharField(max_length=100)
    local_aquifer_name = models.CharField(max_length=100)
    # for all flags ensure null->0 on load
    qw_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    qw_well_chars = models.CharField(max_length=3)
    qw_well_purpose = models.CharField(max_length=15)
    wl_sn_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    # for some reason this field has a couple with 999 but there is no cache use case and not a lookup field
    wl_baseline_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_well_chars = models.CharField(max_length=3)
    wl_well_purpose = models.CharField(max_length=15)
    data_provider = models.CharField(max_length=30)
    qw_sys_name = models.CharField(max_length=50)
    wl_sys_name = models.CharField(max_length=50)
    pk_siteid = models.CharField(max_length=37)
    display_flag = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(1)])
    wl_data_provider = models.CharField(max_length=20)
    qw_data_provider = models.CharField(max_length=20)
    lith_data_provider = models.CharField(max_length=20)
    const_data_provider = models.CharField(max_length=20)
    well_depth = models.DecimalField(max_digits=11, decimal_places=8)
    link = models.CharField(max_length=500)
    wl_well_purpose_notes = models.CharField(max_length=4000)
    qw_well_purpose_notes = models.CharField(max_length=4000)
    insert_user_id = models.CharField(max_length=50)
    update_user_id = models.CharField(max_length=50)
    wl_well_type = models.CharField(max_length=3)
    qw_well_type = models.CharField(max_length=3)
    local_aquifer_cd = models.CharField(max_length=20)
    review_flag = models.CharField(max_length=1)
    site_type = models.CharField(max_length=10)
    aqfr_char = models.CharField(max_length=10)
    horz_method = models.CharField(max_length=300)
    horz_acy = models.CharField(max_length=300)
    alt_method = models.CharField(max_length=300)
    alt_acy = models.CharField(max_length=300)

    insert_date = models.DateTimeField()
    update_date = models.DateTimeField()

    def __str__(self):
        """Default string."""
        # Django does not honor tabs \t, multiple spaces '   ', nor &nbsp for formatting
        str_rep = f"{self.agency_nm}:{self.site_no} display:{self.display_flag} "
        str_rep += f"qw:{self.qw_sn_flag} wl:{self.wl_sn_flag}"
        return str_rep
