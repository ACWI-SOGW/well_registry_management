"""
MonitoringLocation Admin
"""
import csv
import re
from django.contrib import messages
from django.contrib.admin import ModelAdmin, RelatedFieldListFilter, ChoicesFieldListFilter
from django.db.models.functions import Upper
from django.forms import ModelForm, Textarea, ModelChoiceField
from django.http import HttpResponse
from django.urls import path, reverse
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db import connection
from admin_auto_filters.filters import AutocompleteFilter
from ..models import MonitoringLocation, AgencyLookup
from .bulk_upload import BulkUploadView, BulkUploadTemplateView
from .fetch_from_nwis import FetchFromNwisView
from .auto_complete import SiteNoAutoCompleteView

USGS_AGENCY_CD = 'USGS'
tooltips = [{
    'form_field': 'display_flag',
    'tooltip': 'Flag that controls whether the site will be displayed on the NGWMN Data Portal (Yes/No)'
},
    {
        'form_field': 'agency',
        'tooltip': 'The name of the agency or organization that collects, owns andor manages the data. \
 If you don\'t see your agency or organization in the list contact Candice Hopkins (chopkins@usgs.gov).'
    },
    {
        'form_field': 'site_no',
        'tooltip': 'The local unique well or spring identification number or code. We will be requesting water levels \
 and water - quality data from(Organization) -owned  managed databases by this unique well identifier.\
 This identifier may be alphanumeric,but should not contain spaces.'
    },
    {
        'form_field': 'site_name',
        'tooltip': 'The local name of well or spring'
    },
    {
        'form_field': 'country',
        'tooltip': 'The name of the country within which the well or spring resides'
    },
    {
        'form_field': 'state',
        'tooltip': 'The U.S. State or Territory within which the well or spring resides'
    },
    {
        'form_field': 'county',
        'tooltip': 'The name of the county within which the well or spring resides'
    },
    {
        'form_field': 'dec_lat_va',
        'tooltip': 'The site latitude, in decimal degrees to the accuracy of your measurement'
    },
    {
        'form_field': 'dec_long_va',
        'tooltip': 'The site longitude, in decimal degrees (negative for Western Hemisphere) to the accuracy of your\
         measurement'
    },
    {
        'form_field': 'horizontal_datum',
        'tooltip': 'Horizontal reference datum for the latitude and longitude of a well (NAD83,NAD27, WGS84, etc.) \
 If you don\'t see the datum you are looking for in the list contact Candice Hopkins (chopkins@usgs.gov)'
    },
    {
        'form_field': 'horz_method',
        'tooltip': 'A method used to obtain the site\'s latitude and longitude (horizontal location)'
    },
    {
        'form_field': 'horz_acy',
        'tooltip': 'Accuracy of the site\'s latitude and longitude (horizontal location)'
    },
    {
        'form_field': 'alt_method',
        'tooltip': 'A method used to obtain the site\'s latitude and longitude (horizontal location)'
    },
    {
        'form_field': 'alt_acy',
        'tooltip': 'Accuracy of the site\'s latitude and longitude (horizontal location)'
    },
    {
        'form_field': 'alt_va',
        'tooltip': 'Elevation of the land surface at the site'
    },
    {
        'form_field': 'altitude_units',
        'tooltip': 'Units of measure associated with the Altitude field (ft, in, m, cm)'
    },
    {
        'form_field': 'altitude_datum',
        'tooltip': 'Vertical reference datum for the altitude of a well (NGVD29, NAVD88, etc.)'
    },
    {
        'form_field': 'well_depth',
        'tooltip': 'Depth of the well from a specified point of reference'
    },
    {
        'form_field': 'well_depth_units',
        'tooltip': 'Units of measure associated with the well depth field (ft, in, m, cm)'
    },
    {
        'form_field': 'nat_aqfr',
        'tooltip': 'This is the national aquifer designation used by the USGS for U.S. Principal Aquifers.'
    },
    {
        'form_field': 'local_aquifer_name',
        'tooltip': 'The name used for the local aquifer designation'
    },
    {
        'form_field': 'site_type',
        'tooltip': 'The type of groundwater site (Well or Spring)'
    },
    {
        'form_field': 'aqfr_type',
        'tooltip': 'Characteristic of the type of aquifer that the well is completed in (Confined or Unconfined).\
 For the NGWMN, shallow semi-confined wells can be considered to be unconfined if they respond to climatic\
 fluctuations in a relatively short period of time'
    },
    {
        'form_field': 'wl_sn_flag',
        'tooltip': 'Is the well part of the WL network (default is \'Yes\')? All wells, marked as \'Yes\' will be\
 included in the NGWMN WL network. (Yes/No)'
    },
    {
        'form_field': 'wl_network_name',
        'tooltip': 'The system from which water level data from the well or spring will be served to the portal'
    },
    {
        'form_field': 'wl_baseline_flag',
        'tooltip': 'A \'baseline\' period of at least 5 years of data must be available to achieve\
 the \'baseline period\' for a well or spring. Has the baseline period for water levels been satisfied\
 (are there 5 years of data)? (Yes/No) (See the NGWMN Subnetwork Tip Sheet for additional guidance)'
    },
    {
        'form_field': 'wl_well_type',
        'tooltip': 'Three choices are possible: (a) \'Trend\', (b) \'Surveillance\',\
 or (c) \'Special Studies\'. \'Trend\' wells have a monitoring frequency appropriate\
 to determine long-trends and seasonal variability (quarterly), \'Surveillance\' wells are \'synoptic\' snapshots\
 of data used to tied together the \'Trend\' wells. \'Special Studies\' wells are likely to be local areas of depletion\
 or impairment. (See the NGWMN Monitoring Categories Tip Sheet for additional guidance)'
    },
    {
        'form_field': 'wl_well_chars',
        'tooltip': 'The characteristics of the aquifer that the well represents. There are 3 options:\
 (a) \'Background\', (b) \'Suspected/Anticipated Changes\', or (c) \'Known Changes\'.\
 This column is blank if the site is still in the baseline period. (See the NGWMN Subnetwork\
 Tip Sheet for additional guidance)'
    },
    {
        'form_field': 'wl_well_purpose',
        'tooltip': 'A two-category classification to document well\'s original purpose:\
 (a) \'Dedicated Monitoring/Observation\', or (b) \'Other\' (i.e. not a dedicated monitoring well)'
    },
    {
        'form_field': 'wl_well_purpose_notes',
        'tooltip': 'Description of a well\'s purpose or additional notes about the classification of a well\
 within the WL subnetwork'
    },
    {
        'form_field': 'qw_well_purpose_notes',
        'tooltip': 'Description of a well\'s purpose or additional notes about the classification\
 of a well within the WL subnetwork'
    },
    {
        'form_field': 'qw_sn_flag',
        'tooltip': 'Is the well part of the QW network (default is \'Yes\')? All wells, marked as \'Yes\' will be\
 included in the NGWMN QW network. (Yes/No)'
    },
    {
        'form_field': 'qw_well_type',
        'tooltip': 'Three choices are possible: (a) \'Trend\', (b) \'Surveillance\',\
 or (c) \'Special Studies\'. \'Trend\' wells have a monitoring frequency appropriate\
 to determine long-trends and seasonal variability (quarterly), \'Surveillance\' wells\
 are \'synoptic\' snapshots of data used to tied together the \'Trend\' wells. \'Special Studies\' wells\
 are likely to be local areas of depletion or impairment. (See the NGWMN Monitoring Categories Tip Sheet\
 for additional guidance)'
    },
    {
        'form_field': 'qw_network_name',
        'tooltip': 'The system from which water quality data from the well or spring will be served to the portal'
    },
    {
        'form_field': 'qw_well_chars',
        'tooltip': 'The characteristics of the aquifer that the well represents. There are 3 options:\
    (a) \'Background\', (b) \'Suspected/Anticipated Changes\', or (c) \'Known Changes\'.\
 This column is blank if the site is still in the baseline period. (See the NGWMN Subnetwork Tip Sheet for additional\
 guidance)'
    },
    {
        'form_field': 'qw_baseline_flag',
        'tooltip': 'A \'baseline\' period of at least 5 years of data must be available to achieve\
 the \'baseline period\' for a well or spring. Has the baseline period for water quality been satisfied\
 (are there 5 years of data)? (Yes/No) (See the NGWMN Subnetwork Tip Sheet for additional guidance)'
    },
    {
        'form_field': 'qw_well_purpose',
        'tooltip': 'A two-category classification to document well\'s original purpose:\
 (a) \'Dedicated Monitoring/Observation\', or (b) \'Other\' (i.e. not a dedicated monitoring well)'
    },
    {
        'form_field': 'link',
        'tooltip': 'URL to a cooperators site or any other relevant site that contains additional information\
 about the well'
    }
]


def _get_groups(user):
    """Return a list of upper case groups that this user belongs to"""
    return user.groups.all().values_list(Upper('name'), flat=True)

def _has_permission(perm, user, obj=None):
    """Return true if the user has permission, perm, for the obj"""
    if user.is_superuser:
        return True

    return user.has_perm(perm) and (not obj or obj.agency.agency_cd in _get_groups(user))

def _get_usergroups(request):
    user_groups = ""
    if not request.user.is_superuser:
        user_groups = re.search("\[(.*)\]", str(_get_groups(request.user))).group(1)
        user_groups = " where agency.agency_cd IN (" + user_groups + ") "
    return user_groups

def _get_where_clause(request, user_groups):
    where_clause = ""
    sep = ""
    query_params = request.body.decode().split("&")
    for query_param in query_params:
        param = query_param.split("=")
        if param[0] == "_selected_action":
            where_clause += sep + param[1]
            sep = ","
    if len(where_clause) > 0:
        if user_groups == "":
            where_clause = " where registry_monitoringlocation.id IN (" + where_clause + ") \n"
        else:
            where_clause = user_groups + " and registry_monitoringlocation.id IN (" + where_clause + ") \n"
    return where_clause

def _get_monitoringlocation_queryset(request):
    user_groups = _get_usergroups(request)
    where_clause = _get_where_clause(request, user_groups)
    query_ml = "SELECT agency.agency_cd, \n\
        registry_monitoringlocation.site_no as site_no, \n\
        registry_monitoringlocation.site_name as site_name, \n\
        registry_monitoringlocation.dec_lat_va as dec_lat_va, \n\
        registry_monitoringlocation.dec_long_va as dec_long_va, \n\
        registry_monitoringlocation.horizontal_datum_cd, \n\
        registry_monitoringlocation.horz_method as horz_method, \n\
        registry_monitoringlocation.horz_acy as horz_acy, \n\
        registry_monitoringlocation.alt_va as alt_va, \n\
        registry_monitoringlocation.altitude_units as altitude_units, \n\
        registry_monitoringlocation.altitude_datum_cd, \n\
        registry_monitoringlocation.alt_method as alt_method, \n\
        registry_monitoringlocation.alt_acy as alt_acy, \n\
        registry_monitoringlocation.nat_aqfr_cd, \n\
        registry_monitoringlocation.local_aquifer_name as local_aquifer_name, \n\
        '', \n\
        country.country_nm, \n\
        state.state_nm, \n\
        county.county_nm, \n\
        registry_monitoringlocation.well_depth as well_depth, \n\
        registry_monitoringlocation.well_depth_units as well_depth_units, \n\
        registry_monitoringlocation.site_type as site_type, \n\
        registry_monitoringlocation.aqfr_char as aqfr_type, \n\
        registry_monitoringlocation.display_flag as display_flag, \n\
        registry_monitoringlocation.qw_sn_flag as qw_sn_flag, \n\
        registry_monitoringlocation.qw_baseline_flag as qw_baseline_flag, \n\
        registry_monitoringlocation.qw_well_chars as qw_well_chars, \n\
        registry_monitoringlocation.qw_well_type as qw_well_type, \n\
        registry_monitoringlocation.qw_well_purpose as qw_well_purpose, \n\
        registry_monitoringlocation.qw_well_purpose_notes as qw_well_purpose_notes, \n\
        registry_monitoringlocation.qw_sys_name as qw_network_name, \n\
        registry_monitoringlocation.wl_sn_flag as wl_sn_flag, \n\
        registry_monitoringlocation.wl_baseline_flag as wl_baseline_flag, \n\
        registry_monitoringlocation.wl_well_chars as wl_well_chars, \n\
        registry_monitoringlocation.wl_well_type as wl_well_type, \n\
        registry_monitoringlocation.wl_well_purpose as wl_well_purpose, \n\
        registry_monitoringlocation.wl_well_purpose_notes as wl_well_purpose_notes, \n\
        registry_monitoringlocation.wl_sys_name as wl_network_name, \n\
        registry_monitoringlocation.link \n\
        FROM registry.registry_monitoringlocation \n\
        INNER JOIN registry.agency ON (registry.registry_monitoringlocation.agency_cd = \
        registry.agency.agency_cd) \n\
        INNER JOIN registry.country ON (registry.registry_monitoringlocation.country_cd = \
        registry.country.country_cd) \n\
        INNER JOIN registry.state ON (registry.registry_monitoringlocation.state_id = registry.state.id) \n\
        INNER JOIN registry.county ON (registry.registry_monitoringlocation.county_id = registry.county.id) \n\
        INNER JOIN registry.horizontal_datum ON (registry.registry_monitoringlocation.horizontal_datum_cd = \
        registry.horizontal_datum.hdatum_cd) \n\
        INNER JOIN registry.units ON (registry.registry_monitoringlocation.altitude_units = registry.units.unit_id) \n\
        INNER JOIN registry.altitude_datum ON (registry.registry_monitoringlocation.altitude_datum_cd = \
        registry.altitude_datum.adatum_cd) \n\
        INNER JOIN registry.nat_aqfr ON (registry.registry_monitoringlocation.nat_aqfr_cd = \
        registry.nat_aqfr.nat_aqfr_cd)"
    query_ml += where_clause
    query_ml += "ORDER BY registry_monitoringlocation.site_no DESC"

    return query_ml

class MonitoringLocationAdminForm(ModelForm):
    """
    Registry admin form.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.user.is_superuser:
            user_group = _get_groups(self.user)[0]
            agency_field = ModelChoiceField(queryset=AgencyLookup.objects.filter(agency_cd=user_group),
                                            initial=user_group)
            self.fields['agency'] = agency_field
        # With some linked fields, .widget.widget will exist
        # This check will check RelatedFieldWidgetWrapper for attrs .widget.widget first
        # and then .widget if sub widget does not exist
        for item in tooltips:
            form_field = self.fields.get(item['form_field'], None)
            if form_field:
                if isinstance(form_field.widget, RelatedFieldWidgetWrapper):
                    widget = form_field.widget.widget
                else:
                    widget = form_field.widget
                widget.attrs.update({
                    'title': item['tooltip']
                })

    class Meta:
        model = MonitoringLocation
        widgets = {
            'wl_well_purpose_notes': Textarea(),
            'qw_well_purpose_notes': Textarea(),
            'link': Textarea()
        }
        fields = '__all__'

class CountyLookupFilter(AutocompleteFilter):  # pylint: disable=too-few-public-methods
    """
    '''AutoComplete Filter for State/County Filter Filter'''
    """
    title = 'County'  # display title
    field_name = 'county'  # name of the foreign key field
    rel_model = MonitoringLocation

    def get_autocomplete_url(self, request, model_admin):
        """
        '''Get Autocomplete URL''
        """
        rel = self.rel_model._meta.get_field(self.field_name).remote_field
        model = rel.model
        admin_site = model_admin.admin_site
        url_name = '%s:%s_%s_autocomplete'
        state_id = request.GET.get('state__id__exact')
        url = reverse(url_name % (admin_site.name, model._meta.app_label, model._meta.model_name))
        return '%s?state_id=%s' % (url, state_id)

class SiteNoFilter(AutocompleteFilter):
    """
    '''AutoComplete Filter for Site_No'''
    """
    title = 'Site no'
    field_name = 'site_no'
    use_pk_exact = False
    parameter_name = 'site_no__exact'
    template = "admin/site_no-filter.html"

    @staticmethod
    def get_queryset_for_field(model, name):
        # pylint: disable=unused-argument
        """
        '''Get Current Queryset for field''
        """
        return model.objects.get_queryset()

    def get_autocomplete_url(self, request, model_admin):
        # pylint: disable=R0201
        """
        '''Get AutoComplete URL for site_no'''
        """
        return model_admin.custom_urls['siteno_autocomplete']

class SelectListFilter(RelatedFieldListFilter):
    """
    Django admin select list filter to implement a picker for the filter.
    """
    template = "admin/choice_list_filter.html"

class SelectListFilterChoices(ChoicesFieldListFilter):
    """
    Django admin select list filter to implement a picker for the filter.
    """
    template = "admin/choice_list_filter.html"

CSV_HEADERS = [
    'Agency',
    'Site ID',
    'Site Name',
    'Latitude',
    'Longitude',
    'Horiz Datum',
    'Horz Loc Method',
    'Horz Loc Accuracy',
    'Altitude',
    'Altitude Units',
    'Altitude Datum',
    'Altitude Method',
    'Altitude Accuracy',
    'National Aquifer Code',
    'Local Aquifer Name',
    'Local Aquifer Cd',
    'Country',
    'State',
    'County',
    'Well Depth',
    'Well Depth Units',
    'Site Type',
    'Aquifer Type',
    'Display Well?',
    'Water Quality Subnetwork',
    'WQ Baseline Achieved',
    'WQ Well Characteristics',
    'WQ Well Type',
    'WQ Well Purpose',
    'WQ Purpose Notes (Optional)',
    'WQ System Name',
    'Water Level Subnetwork',
    'WL Baseline Achieved',
    'WL Well Characteristics',
    'WL Well Type',
    'WL Well Purpose',
    'WL Purpose Notes (Optional)',
    'WL System Name',
    'Link'
]

def to_yes_no(flag):
    """
    Return true if yes, otherwise no
    """
    return 'Yes' if flag else 'No'

class CountyLookupAdmin(ModelAdmin):
    """
    Django admin model for county lookup
    """
    search_fields = ('county_nm',)

    def get_search_results(self, request, queryset, search_term):
        if 'state_id' in request.GET:
            queryset = queryset.filter(state_id=request.GET['state_id'])
        return super().get_search_results(request, queryset, search_term)

    def has_view_permission(self, request, obj=None):
        """Overrides default implementation"""
        return True

class MonitoringLocationAdmin(ModelAdmin):
    """
    Django admin model for the monitoring location
    """
    form = MonitoringLocationAdminForm
    list_display = ('site_id', 'agency', 'site_no', 'display_flag', 'wl_sn_flag', 'qw_sn_flag',
                    'state', 'nat_aqfr', 'site_name')
    list_filter = (
        ('agency', SelectListFilter),
        ('state', SelectListFilter),
        CountyLookupFilter,
        SiteNoFilter,
        ('nat_aqfr', SelectListFilter),
        'display_flag',
        'update_date'
    )

    actions = ['download_monitoring_locations']

    fields = ['display_flag', 'agency', 'site_no', 'site_name', 'country', 'state', 'county', 'dec_lat_va',
              'dec_long_va', 'horizontal_datum', 'horz_method', 'horz_acy', 'alt_va', 'altitude_units',
              'altitude_datum', 'alt_method', 'alt_acy', 'well_depth', 'well_depth_units', 'nat_aqfr',
              'local_aquifer_name', 'site_type', 'aqfr_type', 'wl_sn_flag', 'wl_network_name', 'wl_baseline_flag',
              'wl_well_type', 'wl_well_chars', 'wl_well_purpose', 'wl_well_purpose_notes', 'qw_sn_flag',
              'qw_network_name', 'qw_baseline_flag', 'qw_well_type', 'qw_well_chars', 'qw_well_purpose',
              'qw_well_purpose_notes', 'link'
              ]

    custom_urls = {
        'siteno_autocomplete': 'siteno/autocomplete/'
    }

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency.agency_cd}:{obj.site_no}"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk_upload/',
                 self.admin_site.admin_view(BulkUploadView.as_view()),
                 name='bulk_upload'),
            path('bulk_upload_template/',
                 self.admin_site.admin_view(BulkUploadTemplateView.as_view()),
                 name='bulk_upload_template'),
            path('fetch_from_nwis/',self.admin_site.admin_view(FetchFromNwisView.as_view()),name='fetch_from_nwis'),
            path(self.custom_urls['siteno_autocomplete'],
                 self.admin_site.admin_view(SiteNoAutoCompleteView.as_view(model_admin=self)),
                 name='siteno_autocomplete')
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if obj and obj.agency.agency_cd == USGS_AGENCY_CD:
            fields = ['site_no', 'site_name', 'country', 'state', 'county', 'dec_lat_va', 'dec_long_va',
                      'horizontal_datum', 'horz_method', 'horz_acy', 'alt_va', 'altitude_units',
                      'altitude_datum', 'alt_method', 'alt_acy', 'well_depth', 'well_depth_units', 'nat_aqfr',
                      'local_aquifer_name', 'site_type', 'aqfr_type']
        return fields

    def save_model(self, request, obj, form, change):
        if not obj.insert_user:
            obj.insert_user = request.user
        obj.update_user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Overrides default implementation"""
        return MonitoringLocation.objects.all() if request.user.is_superuser \
            else MonitoringLocation.objects.filter(agency__in=_get_groups(request.user))

    def download_monitoring_locations(self, request, queryset):
        """
        Returns a response which contains a csv with the requested monitoring locations
        :param request:
        :param queryset: MonitoringLocation queryset
        :return: HttpResponse
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="monitoring_locations.csv"'

        query_monitoring_location = _get_monitoringlocation_queryset(request)
        queryset_raw = connection.cursor()
        queryset_raw.execute(query_monitoring_location)
        writer = csv.writer(response)
        writer.writerow(CSV_HEADERS)
        query_count = 0
        for monitoring_location in queryset_raw.fetchall():
            writer.writerow(monitoring_location)
            query_count = query_count + 1
        self.message_user(
            request, f'Downloaded {query_count} monitoring locations', messages.SUCCESS)
        return response

    download_monitoring_locations.short_description = 'Download selected monitoring locations'

    def has_view_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.view_monitoringlocation', request.user, obj)

    def has_add_permission(self, request):
        """Overrides default implementation"""
        return _has_permission('registry.add_monitoringlocation', request.user)

    def has_change_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.change_monitoringlocation', request.user, obj)

    def has_delete_permission(self, request, obj=None):
        """Overrides default implementation"""
        return _has_permission('registry.delete_monitoringlocation', request.user, obj)

    def changelist_view(self, request, extra_context=None):
        self.message_user(request,
                          'Note: additions/changes to monitoring locations may\
                          take up to a day to appear in the NGWMN Data Portal')
        return super().changelist_view(request, extra_context=extra_context)
