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
    HorizontalDatumLookup, NatAqfrLookup, StateLookup, UnitsLookup
from .utils import parse_rdb

# this is the Django property for the admin main page header
admin.site.site_header = 'NGWMN Well Registry Administration'
admin.site.login_template = 'registration/login.html'


class MonitoringLocationAdminForm(forms.ModelForm):
    """
    Registry admin form.
    """
    def clean(self):
        """
        Override form clean to do multi field validation
        """
        cleaned_data = super().clean()
        if (cleaned_data['display_flag'] and cleaned_data['wl_sn_flag']) and \
            (not cleaned_data['wl_baseline_flag'] or cleaned_data['wl_well_type'] == ''
             or cleaned_data['wl_well_purpose'] == ''):
            raise forms.ValidationError(
                'If the well is In WL sub-network, then you must check WL Baseline \
                and enter a WL well type and WL well purpose')

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
    site_no = CharField(label='Enter NWIS site number to add to the well registry', max_length=16)
    overwrite = ChoiceField(label='Do you want to overwrite the site\'s meta data', choices=('Yes', 'No'))

class FetchFromNwisView(FormView):
    template_name = 'admin/fetch_from_nwis.html'
    form_class = FetchForm

    def _validate_site(self, site_data):
        if site_data['site_tp_cd'] not in ['GW', 'SP']:
            return False, 'Site is not a Well or Spring (site_tp_cd is not GW or SP)'
        if not site_data['well_depth_va']:
            return False, 'Site is missing a well depth'
        return True, 'Valid site'

    def _get_monitoring_location(self, site_data, existing_ml):

        AQFR_TYPE_CD_TO_NWIS = {
            'C': 'CONFINED',
            'M': 'CONFINED',
            'N': 'UNCONFINED',
            'U': 'UNCONFINED',
            'X': 'CONFINED'
        }
        existing_ml_dict = {k: v for k, v in existing_ml.__dict__.iteritems() if v is not None}

        country = CountryLookup.objects.get(country_cd=site_data['country_cd'])
        state = StateLookup.objects.get(state_cd=site_data['state_cd'], country_cd=country)

        new_ml = MonitoringLocation(
            agency=AgencyLookup.objects.get(agency_cd=site_data['agency_cd']),
            site_no=site_data['site_no'],
            site_name=site_data['station_nm'],
            country=country,
            state=state,
            county=CountyLookup.objects.get(country_cd=country,
                                            state_id=state,
                                            county_cd=site_data['county_cd']),
            dec_lat_va=site_data['dec_lat_va'],
            dec_long_va=site_data['dec_long_va'],
            horizontal_datum=HorizontalDatumLookup.objects.get(hdatum_cd=site_data['dec_coord_datum_cd']),
            horz_method=site_data['coord_meth_cd'],
            horz_acy=site_data['coord_acy_cd'],
            alt_va=site_data['alt_va'],
            altitude_datum=AltitudeDatumLookup.objects.get(adatum_cd=site_data['alt_datum_cd']),
            alt_method=site_data['alt_meth_cd'],
            alt_acy=site_data['alt_acy_va'],
            well_depth=site_data['well_depth_va'],
            nat_aqfr=NatAqfrLookup.objects.get(nat_aqfr_cd=site_data['nat_aqfr_cd']),
            site_type='SPRING' if site_data['site_tp_cd'] == 'SP' else 'GW',
            aqfr_type=AQFR_TYPE_CD_TO_NWIS[site_data['aqfr_type_cd']],
        )

        return new_ml.__dict__.update(existing_ml_dict)

    def form_valid(self, form):
        site_no = form.cleaned_data['site_no']
        overwrite = form.cleaned_data['overwrite']
        agency = AgencyLookup.objects.get(agency_cd='USGS')

        context = self.get_context_data()

        site_exists = MonitoringLocation.objects.filter(site_no=site_no, agency=agency).exists()

        if site_exists and overwrite == None:
            context['show_overwrite'] = True

        elif site_exists and overwrite == 'No':
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
                data = [datum for datum in parse_rdb(resp.iter_lines(decode_unicode=True))]
                if len(data):
                    existing_ml = MonitoringLocation.objects.get(site_no=site_no, agency=agency) if (
                                site_exists and overwrite) else None
                    if site_exists and overwrite == 'Yes':
                        existing_ml = MonitoringLocation.objects.get(site_no=site_no, agency=agency)
                    else:
                        valid, message = self._validate_site(data[0])
                        if valid:
                            ml = self._get_monitoring_location(data[0])

                            ml.save()
                            return redirect(reverse('admin:registry_monitoringlocation_change', args=(ml.id,)))
                        else:
                            context['request_response'] = message
                else:
                    context['request_response'] = f'No site exists for {site_no}'
            elif resp.status_code == 404:
                context['request_response'] = f'No site exists for {site_no}'
            else:
                context['request_response'] = f'Service request to NWIS failed with status {resp.status_code}'

        return render(self.request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        urls = super(MonitoringLocationAdmin, self).get_urls()
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


admin.site.site_url = None
admin.site.enable_nav_sidebar = False
admin.site.register(MonitoringLocation, MonitoringLocationAdmin)
