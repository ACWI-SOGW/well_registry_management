"""
MonitoringLocation Admin
"""
import csv

from django.contrib import messages
from django.contrib.admin import ModelAdmin, RelatedFieldListFilter
from django.db.models.functions import Upper
from django.forms import ModelForm, Textarea, ModelChoiceField, HiddenInput
from django.http import HttpResponse
from django.urls import path

from ..models import MonitoringLocation, AgencyLookup, CountryLookup, CountyLookup, StateLookup
from .bulk_upload import BulkUploadView, BulkUploadTemplateView
from .fetch_from_nwis import FetchFromNwisView


def _get_groups(user):
    """Return a list of upper case groups that this user belongs to"""
    return user.groups.all().values_list(Upper('name'), flat=True)


def _has_permission(perm, user, obj=None):
    """Return true if the user has permission, perm, for the obj"""
    if user.is_superuser:
        return True

    return user.has_perm(perm) and (not obj or obj.agency.agency_cd in _get_groups(user))


class MonitoringLocationAdminForm(ModelForm):
    """
    Registry admin form.
    """

    # pylint: disable=E1101
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.user.is_superuser:
            agency_field = ModelChoiceField(queryset=AgencyLookup.objects.all(),
                                            widget=HiddenInput,
                                            initial=AgencyLookup.objects.get(agency_cd=_get_groups(self.user)[0]))
            self.fields['agency'] = agency_field

    class Meta:
        model = MonitoringLocation
        widgets = {
            'wl_well_purpose_notes': Textarea(),
            'qw_well_purpose_notes': Textarea(),
            'link': Textarea()
        }
        fields = '__all__'


class SelectListFilter(RelatedFieldListFilter):
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
    return 'Yes' if flag else 'No'


def get_row(monitoring_location):
    return [
        monitoring_location.agency,
        monitoring_location.site_no,
        monitoring_location.site_name,
        monitoring_location.dec_lat_va,
        monitoring_location.dec_long_va,
        monitoring_location.horizontal_datum,
        monitoring_location.horz_method,
        monitoring_location.horz_acy,
        monitoring_location.alt_va,
        monitoring_location.altitude_units,
        monitoring_location.altitude_datum,
        monitoring_location.alt_method,
        monitoring_location.alt_acy,
        monitoring_location.nat_aqfr.nat_aqfr_cd if monitoring_location.nat_aqfr else '',
        monitoring_location.local_aquifer_name,
        '',
        monitoring_location.country.country_nm if monitoring_location.country else '',
        monitoring_location.state.state_nm if monitoring_location.state else '',
        monitoring_location.county.county_nm if monitoring_location.county else '',
        monitoring_location.well_depth,
        monitoring_location.well_depth_units,
        monitoring_location.site_type,
        monitoring_location.aqfr_type,
        to_yes_no(monitoring_location.display_flag),
        to_yes_no(monitoring_location.qw_sn_flag),
        to_yes_no(monitoring_location.qw_baseline_flag),
        monitoring_location.qw_well_chars,
        monitoring_location.qw_well_type,
        monitoring_location.qw_well_purpose,
        monitoring_location.qw_well_purpose_notes,
        monitoring_location.qw_network_name,
        to_yes_no(monitoring_location.wl_sn_flag),
        to_yes_no(monitoring_location.wl_baseline_flag),
        monitoring_location.wl_well_chars,
        monitoring_location.wl_well_type,
        monitoring_location.wl_well_purpose,
        monitoring_location.wl_well_purpose_notes,
        monitoring_location.wl_network_name,
        monitoring_location.link
    ]


class MonitoringLocationAdmin(ModelAdmin):
    """
    Django admin model for the monitoring location
    """
    form = MonitoringLocationAdminForm
    list_display = ('site_id', 'agency', 'site_no', 'display_flag', 'wl_sn_flag', 'qw_sn_flag',
                    'insert_date', 'update_date')
    list_filter = (('agency', SelectListFilter), 'site_no', 'update_date')

    actions = ['download_monitoring_locations']

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency.agency_cd}:{obj.site_no}"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk_upload/', self.admin_site.admin_view(BulkUploadView.as_view()), name='bulk_upload'),
            path('bulk_upload_template/', self.admin_site.admin_view(BulkUploadTemplateView.as_view()),
                 name='bulk_upload_template'),
            path('fetch_from_nwis/', self.admin_site.admin_view(FetchFromNwisView.as_view()), name='fetch_from_nwis')
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.user = request.user
        return form

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

        writer = csv.writer(response)
        writer.writerow(CSV_HEADERS)
        for ml in queryset.iterator():
            writer.writerow(get_row(ml))

        self.message_user(request, f'Downloaded {queryset.count()} monitoring locations', messages.SUCCESS)
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
        extra_context = extra_context or {}
        extra_context['show_fetch_from_nwis_view'] = request.user.is_superuser or 'USGS' in _get_groups(request.user)
        return super().changelist_view(request, extra_context=extra_context)
