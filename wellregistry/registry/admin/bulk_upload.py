"""
Custom bulk upload view
"""

import csv
from decimal import Decimal
import io

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import Form, FileField
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from ..models import MonitoringLocation, AgencyLookup, AltitudeDatumLookup, HorizontalDatumLookup, NatAqfrLookup, \
    UnitsLookup, CountyLookup, StateLookup, CountryLookup

def _get_lookup(model, field_name, value):
    qs = model.objects.filter(**({field_name: value}))
    if len(qs) == 0:
        return None
    return qs[0]

def _get_state_lookup(country, state_name):
    if not country:
        return None
    else:
        qs = StateLookup.objects.filter(country_cd=country, state_nm=state_name)
        if len(qs) == 0:
            return None
        return qs[0]

def _get_county_lookup(country, state, county_name):
    if not country or not state:
        return None
    else:
        qs = CountyLookup.objects.filter(county_nm=county_name, state_id=state, country_cd=country)
        if len(qs) == 0:
            return None
        return qs[0]


def _get_monitoring_location(row, user):
    """
    Parses the list of strings that represent a row in the bulk upload template, validates and
    returns a MonitoringLocation instance. Raises Validation_Error if the row can not be converted
    :list of strings row:
    :User user
    :return: MonitoringLocation
    """
    if len(row) < 39:
        raise ValidationError('Does not contain the correct number of columns', code='invalid file')

    local_aquifer_code = f' ({row[15]})' if row[15] else ''
    country = _get_lookup(CountryLookup, 'country_nm', row[16])
    state = _get_state_lookup(country, row[17])

    monitoring_location = MonitoringLocation(
        agency=_get_lookup(AgencyLookup, 'agency_cd', row[0]),
        site_no=row[1],
        site_name=row[2],
        dec_lat_va=Decimal(row[3]),
        dec_long_va=Decimal(row[4]),
        horizontal_datum=_get_lookup(HorizontalDatumLookup, 'hdatum_cd',row[5]),
        horz_method=row[6],
        horz_acy=row[7],
        alt_va=Decimal(row[8]),
        altitude_units=_get_lookup(UnitsLookup, 'unit_desc', row[9]),
        altitude_datum=_get_lookup(AltitudeDatumLookup, 'adatum_cd', row[10]),
        alt_method=row[11],
        alt_acy=row[12],
        nat_aqfr=_get_lookup(NatAqfrLookup, 'nat_aqfr_cd', row[13]),
        local_aquifer_name=f'{row[14]}{local_aquifer_code}',
        country=country,
        state=state,
        county=_get_county_lookup(country, state, row[18]),
        well_depth=Decimal(row[19]),
        well_depth_units=_get_lookup(UnitsLookup, 'unit_desc', row[20]),
        site_type=row[21],
        aqfr_type=row[22],
        display_flag=True if row[23] == 'Yes' else False,
        qw_sn_flag=True if row[24] == 'Yes' else False,
        qw_baseline_flag=True if row[25] == 'Yes' else False,
        qw_well_chars=row[26],
        qw_well_type=row[27],
        qw_well_purpose=row[28],
        qw_well_purpose_notes=row[29],
        qw_network_name=row[30],
        wl_sn_flag=True if row[31] == 'Yes' else False,
        wl_baseline_flag=True if row[32] == 'Yes' else False,
        wl_well_chars=row[33],
        wl_well_type=row[34],
        wl_well_purpose=row[35],
        wl_well_purpose_notes=row[36],
        wl_network_name=row[37],
        link=row[38],
        insert_user=user,
        update_user=user
    )
    monitoring_location.full_clean()
    return monitoring_location


class BulkUploadForm(Form):
    file = FileField(label='Upload monitoring locations from csv')


class BulkUploadView(View):
    form_class = BulkUploadForm
    template_name = 'admin/bulk_upload.html'

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.form_class()
        }
        context.update(dict(admin.site.each_context(self.request)))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES['file']
        data_set = csv_file.read().decode('UTF-8')
        data_stream = io.StringIO(data_set)
        # Skip header
        next(data_stream)
        monitoring_locations = []
        error_messages = []
        row_index = 1
        for row in csv.reader(data_stream):
            row_index = row_index + 1
            try:
                monitoring_locations.append(_get_monitoring_location(row, request.user))
            except ValidationError as error:
                error_messages.append((row_index, error.message_dict))
        if len(error_messages) == 0:
            try:
                MonitoringLocation.objects.bulk_create(monitoring_locations)
            except BaseException as error:
                error_messages.append('Error when creating objects')
            else:
                return redirect(reverse('admin:registry_monitoringlocation_changelist'))
        context = {
            'form': self.form_class(),
            'errors': error_messages
        }
        context.update(dict(admin.site.each_context(self.request)))
        return render(request, self.template_name, context)
