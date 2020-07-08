"""
Well Registry ORM object.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class CountryLookup(models.Model):
    """
    Country lookup table for the Registry app.

    Used to populate drop downs.

    """
    country_cd = models.CharField(max_length=10, primary_key=True)
    country_nm = models.CharField(max_length=200)

    def __str__(self):
        return self.country_nm


class Registry(models.Model):
    """
    Django Registry Model.

    # python manage.py makemigrations and migrate
    """

    # these will become lookups with                    foreign keys
    agency_cd = models.CharField(max_length=20)      # AGENCY_LOV.AGENCY_CD

    well_depth_units = models.IntegerField()          # UNITS_DIM.UNIT_ID
    alt_datum_cd = models.CharField(max_length=10, blank=True)    # ALT_DATUM_DIM.ADATUM_CD
    alt_units = models.IntegerField()                 # UNITS_DIM.UNIT_ID
    horz_datum = models.CharField(max_length=10, blank=True)      # HORZ_DATUM_DIM.HDATUM_CD
    nat_aquifer_cd = models.CharField(max_length=10, blank=True)  # NAT_AQFR.NAT_AQFR_CD
    country_cd = models.ForeignKey(CountryLookup, on_delete=models.CASCADE, blank=True)       # COUNTRY.COUNTRY_CD
    state_cd = models.CharField(max_length=2, blank=True)         # STATE.STATE_CD and STATE.COUNTRY_CD
    county_cd = models.CharField(max_length=3, blank=True)        # COUNTY.COUNTY_CD and COUNTY.STATE_CD and COUNTY.COUNTRY_CD

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
        str_rep = f'{self.agency_cd}:{self.site_no}'
        return str_rep
