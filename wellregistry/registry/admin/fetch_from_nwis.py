"""
Custom fetch from nwis form and view for the Django admin
"""

import requests

from django.conf import settings
from django.contrib import admin
from django.forms import Form, CharField, ChoiceField
from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views.generic.edit import FormView

from wellregistry import nwis_aquifer_lookups

from ..models import MonitoringLocation, AgencyLookup, AltitudeDatumLookup, UnitsLookup, HorizontalDatumLookup, \
    NatAqfrLookup, CountryLookup, StateLookup, CountyLookup
from ..utils import parse_rdb


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
    def _get_lcl_aqfr_name(list_aqr_lookups, aqfr_cd, state_cd):
        try:
            for item in list_aqr_lookups:
                if item['Aqfr_Cd'] == aqfr_cd and item['State_Cd'] == state_cd:
                    aqfr_nm =  item['Aqfr_Nm']

        except KeyError:
            print("key not found in dictionary")
        return Aqfr_Nm

    @staticmethod
    def _get_monitoring_location(self, site_data, user):
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
            monitoring_location.insert_user = user

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
        monitoring_location.altitude_units=UnitsLookup.objects.get(unit_id=1)
        monitoring_location.alt_method = site_data['alt_meth_cd']
        monitoring_location.alt_acy = site_data['alt_acy_va']
        monitoring_location.well_depth = float(site_data['well_depth_va'])
        monitoring_location.well_depth_units = UnitsLookup.objects.get(unit_id=1)
        monitoring_location.nat_aqfr = NatAqfrLookup.objects.get(nat_aqfr_cd=site_data['nat_aqfr_cd'])
        monitoring_location.local_aquifer_name = \
            self._get_lcl_aqfr_name(nwis_aquifer_lookups, site_data['aqfr_cd'], site_data['state_cd'])
        monitoring_location.site_type = 'SPRING' if site_data['site_tp_cd'] == 'SP' else 'WELL'
        monitoring_location.aqfr_type = nwis_aqfr_type_cd_to_aqfr_type[site_data['aqfr_type_cd']]
        monitoring_location.update_user = user

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
                        monitoring_location = self._get_monitoring_location(self,site, self.request.user)

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
