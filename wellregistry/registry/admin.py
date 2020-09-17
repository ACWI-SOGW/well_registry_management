"""
Django Registry Administration.
"""

import requests

from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models.functions import Upper
from django.forms import Form, CharField, ChoiceField
from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.urls import path
from django.urls.base import reverse

from .models import MonitoringLocation, AgencyLookup, AltitudeDatumLookup, CountyLookup, CountryLookup, \
    HorizontalDatumLookup, NatAqfrLookup, StateLookup
from .utils import parse_rdb

# this is the Django property for the admin main page header
admin.site.site_header = 'NGWMN Well Registry Administration'
admin.site.login_template = 'registration/login.html'


class MonitoringLocationAdminForm(forms.ModelForm):
    """
    Registry admin form.
    """
    class Meta:
        model = MonitoringLocation
        widgets = {
            'wl_well_purpose_notes': forms.Textarea(),
            'qw_well_purpose_notes': forms.Textarea(),
            'link': forms.Textarea()
        }
        fields = '__all__'


def _get_groups(user):
    """Return a list of upper case groups that this user belongs to"""
    return user.groups.all().values_list(Upper('name'), flat=True)


def _has_permission(perm, user, obj=None):
    """Return true if the user has permission, perm, for the obj"""
    if user.is_superuser:
        return True

    return user.has_perm(perm) and (not obj or obj.agency.agency_cd in _get_groups(user))


class SelectListFilter(admin.RelatedFieldListFilter):
    """
    Django admin select list filter to implement a picker for the filter.
    """
    template = "admin/choice_list_filter.html"


class FetchForm(Form):
    """
    Implements the form in the fetch_from_nwis view. Renders form fields
    needed to load monitoring location data from NWIS
    """
    site_no = CharField(label='Enter NWIS site number to add to the well registry', max_length=16)
    overwrite = ChoiceField(label='Do you want to overwrite the site\'s meta data',
                            choices=(('', '------'), ('y', 'Yes'), ('n', 'No')),
                            required=False)


class FetchFromNwisView(FormView):
    """
    Implements the fetch_from_nwis view. The view renders a form that is used
    to enter information. The site is then retrieved from NWIS and if successful
    forward to the change page for that site.
    """
    template_name = 'admin/fetch_from_nwis.html'
    form_class = FetchForm

    @staticmethod
    def _validate_site(site_data):
        if site_data['site_tp_cd'] not in ['GW', 'SP']:
            return False, 'Site is not a Well or Spring (site_tp_cd is not GW or SP)'
        if not site_data['well_depth_va']:
            return False, 'Site is missing a well depth'
        return True, 'Valid site'

    @staticmethod
    def _get_monitoring_location(site_data):
        """
        Returns a MonitoringLocation. If the site_no and agency_cd from site_data already
        exists, then update the MonitoringLocation instance. Otherwise create a new instance.

        :param site_data: dictionary of fields retrieved from NWIS site service
        :return: MonitoringLocation
        """
        nwis_aqfr_type_cd_to_aqfr_type = {
            'C': 'CONFINED',
            'M': 'CONFINED',
            'N': 'UNCONFINED',
            'U': 'UNCONFINED',
            'X': 'CONFINED',
            '': ''
        }

        agency = AgencyLookup.objects.get(agency_cd=site_data['agency_cd'])
        country = CountryLookup.objects.get(country_cd=site_data['country_cd'])
        state = StateLookup.objects.get(state_cd=site_data['state_cd'], country_cd=country)

        if MonitoringLocation.objects.filter(agency=agency, site_no=site_data['site_no']).exists():
            monitoring_location = MonitoringLocation.objects.get(agency=agency, site_no=site_data['site_no'])
        else:
            monitoring_location = MonitoringLocation()
            monitoring_location.agency = agency
            monitoring_location.site_no = site_data['site_no']

        monitoring_location.site_name = site_data['station_nm']
        monitoring_location.country = country
        monitoring_location.state = state
        monitoring_location.county = CountyLookup.objects.get(
            country_cd=country,
            state_id=state,
            county_cd=site_data['county_cd']
        )
        monitoring_location.dec_lat_va = float(site_data['dec_lat_va'])
        monitoring_location.dec_long_va = float(site_data['dec_long_va'])
        monitoring_location.horizontal_datum = \
            HorizontalDatumLookup.objects.get(hdatum_cd=site_data['dec_coord_datum_cd'])
        monitoring_location.horz_method = site_data['coord_meth_cd']
        monitoring_location.horz_acy = site_data['coord_acy_cd']
        monitoring_location.alt_va = float(site_data['alt_va'])
        monitoring_location.altitude_datum = AltitudeDatumLookup.objects.get(adatum_cd=site_data['alt_datum_cd'])
        monitoring_location.alt_method = site_data['alt_meth_cd']
        monitoring_location.alt_acy = site_data['alt_acy_va']
        monitoring_location.well_depth = float(site_data['well_depth_va'])
        monitoring_location.nat_aqfr = NatAqfrLookup.objects.get(nat_aqfr_cd=site_data['nat_aqfr_cd'])
        monitoring_location.site_type = 'SPRING' if site_data['site_tp_cd'] == 'SP' else 'WELL'
        monitoring_location.aqfr_type = nwis_aqfr_type_cd_to_aqfr_type[site_data['aqfr_type_cd']]

        return monitoring_location

    def form_valid(self, form):
        """
        Overrides the ModelAdmin form_valid method
        :param form: FetchForm
        :return: HttpResponse
        """
        site_no = form.cleaned_data['site_no']
        overwrite = form.cleaned_data['overwrite']
        agency = AgencyLookup.objects.get(agency_cd='USGS')

        context = self.get_context_data()

        site_exists = MonitoringLocation.objects.filter(site_no=site_no, agency=agency).exists()
        if site_exists and not overwrite:
            context['show_overwrite'] = True

        elif site_exists and overwrite == 'n':
            return redirect(
                reverse('admin:registry_monitoringlocation_change',
                        args=(MonitoringLocation.objects.get(site_no=site_no, agency=agency).id,))
            )
        else:
            resp = requests.get(settings.NWIS_SITE_SERVICE_ENDPOINT, params={
                'format': 'rdb',
                'siteOutput': 'expanded',
                'sites': site_no,
                'siteStatus': 'all'
            })
            if resp.status_code == 200:
                sites = parse_rdb(resp.iter_lines(decode_unicode=True))
                try:
                    site = next(sites)
                except StopIteration:
                    context['request_response'] = f'No site exists for {site_no}'
                else:
                    valid, message = self._validate_site(site)
                    if valid:
                        monitoring_location = self._get_monitoring_location(site)

                        monitoring_location.save()
                        return redirect(reverse('admin:registry_monitoringlocation_change',
                                                args=(monitoring_location.id,)))

                    context['request_response'] = message

            elif resp.status_code == 404:
                context['request_response'] = f'No site exists for {site_no}'
            else:
                context['request_response'] = f'Service request to NWIS failed with status {resp.status_code}'

        return render(self.request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # This adds admin specific context
        context.update(dict(admin.site.each_context(self.request)))
        return context


class MonitoringLocationAdmin(admin.ModelAdmin):
    """
    Django admin model for the registry application
    """
    form = MonitoringLocationAdminForm
    list_display = ('site_id', 'agency', 'site_no', 'display_flag', 'wl_sn_flag', 'qw_sn_flag',
                    'insert_date', 'update_date')
    list_filter = (('agency', SelectListFilter), 'site_no', 'update_date')

    @staticmethod
    def site_id(obj):
        """Constructs a site id from agency code and site number."""
        # The obj field agency_cd is the AgencyLovLookup model, retrieve agency_cd from the model
        return f"{obj.agency.agency_cd}:{obj.site_no}"

    def get_urls(self):
        urls = super().get_urls()
        nwis_fetch_url = [
            path('fetch_from_nwis/', self.admin_site.admin_view(FetchFromNwisView.as_view()), name='fetch_from_nwis')
        ]
        return nwis_fetch_url + urls

    def save_model(self, request, obj, form, change):
        if not obj.insert_user:
            obj.insert_user = request.user
        obj.update_user = request.user

        if not obj.agency and not request.user.is_superuser:
            obj.agency = AgencyLookup.objects.get(agency_cd=_get_groups(request.user)[0])

        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """Overrides default implementation"""
        return ('agency',) if not request.user.is_superuser else ()

    def get_queryset(self, request):
        """Overrides default implementation"""
        return MonitoringLocation.objects.all() if request.user.is_superuser \
            else MonitoringLocation.objects.filter(agency__in=_get_groups(request.user))

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
        extra_context['show_fetch_from_nwis_view'] = 'USGS' in _get_groups(request.user)
        return super().changelist_view(request, extra_context=extra_context)


admin.site.site_url = None
admin.site.enable_nav_sidebar = False
admin.site.register(MonitoringLocation, MonitoringLocationAdmin)
