"""
Well Registry ORM object.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class AgencyLovLookup(models.Model):
    """Model definition for the agency_lov table, lookup only"""
    agency_cd = models.CharField(max_length=50, primary_key=True)
    agency_nm = models.CharField(max_length=150, blank=True, null=True)
    org_type = models.CharField(max_length=50, blank=True, null=True)
    agency_med = models.CharField(max_length=200, blank=True, null=True)
    state_cd = models.CharField(max_length=5, blank=True, null=True)
    agency_link = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'agency_lov'

    def __str__(self):
        return self.agency_nm


class AltDatumDimLookup(models.Model):
    """Model definition for the alt_datum_dim table, lookup only"""
    adatum_cd = models.CharField(max_length=10, primary_key=True)
    adatum_desc = models.CharField(max_length=100, blank=True, null=True)
    datum_type = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'alt_datum_dim'

    def __str__(self):
        return self.adatum_desc


class CountryLookup(models.Model):
    """Model definition for the country table, lookup only"""
    country_cd = models.CharField(primary_key=True, max_length=2)
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
    county_max_lat_va = models.CharField(max_length=11)
    county_min_lat_va = models.CharField(max_length=11)
    county_max_long_va = models.CharField(max_length=12)
    county_min_long_va = models.CharField(max_length=12)
    county_max_alt_va = models.CharField(max_length=8)
    county_min_alt_va = models.CharField(max_length=8)
    county_md = models.CharField(max_length=8)

    class Meta:
        db_table = 'county'
        unique_together = (('country_cd', 'state_cd', 'county_cd'),)

    def __str__(self):
        return self.county_nm

class HorzDatumDimLookup(models.Model):
    """Model definition for the horz_datum_dim table, lookup only"""
    hdatum_cd = models.CharField(primary_key=True, max_length=10)
    hdatum_desc = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        db_table = 'horz_datum_dim'

    def __str__(self):
        return self.hdatum_desc


class NatAqfrLookup(models.Model):
    """Model definition for the nat_aqfr table, lookup only"""
    nat_aqfr_cd = models.CharField(primary_key=True, max_length=10)
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
    state_post_cd = models.CharField(max_length=2)
    state_max_lat_va = models.CharField(max_length=11, blank=True, null=True)
    state_min_lat_va = models.CharField(max_length=11, blank=True, null=True)
    state_max_long_va = models.CharField(max_length=12, blank=True, null=True)
    state_min_long_va = models.CharField(max_length=12, blank=True, null=True)
    state_max_alt_va = models.CharField(max_length=8, blank=True, null=True)
    state_min_alt_va = models.CharField(max_length=8, blank=True, null=True)
    state_md = models.CharField(max_length=8)

    class Meta:
        db_table = 'state'
        unique_together = (('country_cd', 'state_cd'),)

    def __str__(self):
        return self.state_nm


class UnitsDimLookup(models.Model):
    """Model definition for the units_dim table, lookup only"""
    unit_id = models.FloatField(primary_key=True)
    unit_desc = models.CharField(max_length=20, blank=True, null=True)
    unit_abrev = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'units_dim'

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
    agency_cd = models.ForeignKey(AgencyLovLookup, on_delete=models.PROTECT) # AGENCY_LOV.AGENCY_CD
    well_depth_units = models.ForeignKey(UnitsDimLookup, related_name='+',
                                         on_delete=models.PROTECT) # UNITS_DIM.UNIT_ID
    alt_datum_cd = models.ForeignKey(AltDatumDimLookup, on_delete=models.PROTECT) # ALT_DATUM_DIM.ADATUM_CD
    alt_units = models.ForeignKey(UnitsDimLookup, on_delete=models.PROTECT) # UNITS_DIM.UNIT_ID
    horz_datum = models.ForeignKey(HorzDatumDimLookup, on_delete=models.PROTECT) # HORZ_DATUM_DIM.HDATUM_CD
    nat_aquifer_cd = models.ForeignKey(NatAqfrLookup, on_delete=models.PROTECT)  # NAT_AQFR.NAT_AQFR_CD
    country_cd = models.ForeignKey(CountryLookup, on_delete=models.PROTECT)  # COUNTRY.COUNTRY_CD
    state_cd = models.ForeignKey(StateLookup, on_delete=models.PROTECT) # STATE.STATE_CD and STATE.COUNTRY_CD
    county_cd = models.ForeignKey(CountyLookup, on_delete=models.PROTECT) # COUNTY.{country_cd,state_cd,county_cd'}

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
