"""
Well Registry ORM object.

"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Registry(models.Model):
    """
    Django Registry Model.

    # python manage.py makemigrations and migrate
    These fields names are nasty but they are to match the original.
    We could refactor later.

    """
    # these will become lookups with                    foreign keys
    agency_cd = models.CharField(max_length=20)       # AGENCY_LOV.AGENCY_CD
    well_depth_units = models.IntegerField()          # UNITS_DIM.UNIT_ID
    alt_datum_cd = models.CharField(max_length=10)    # ALT_DATUM_DIM.ADATUM_CD
    alt_units = models.IntegerField()                 # UNITS_DIM.UNIT_ID
    horz_datum = models.CharField(max_length=10)      # HORZ_DATUM_DIM.HDATUM_CD
    nat_aquifer_cd = models.CharField(max_length=10)  # NAT_AQFR.NAT_AQFR_CD
    country_cd = models.CharField(max_length=2)       # COUNTRY.COUNTRY_CD
    state_cd = models.CharField(max_length=2)         # STATE.STATE_CD and STATE.COUNTRY_CD
    county_cd = models.CharField(max_length=3)        # COUNTY.COUNTY_CD and COUNTY.STATE_CD and COUNTY.COUNTRY_CD

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
