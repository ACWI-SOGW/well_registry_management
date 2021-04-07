"""
Custom bulk upload view
"""

import csv
from decimal import Decimal
import io

from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import Form, FileField
from django.http import HttpResponse
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
    qs = StateLookup.objects.filter(country_cd=country, state_nm=state_name)
    if len(qs) == 0:
        return None
    return qs[0]


def _get_county_lookup(country, state, county_name):
    if not country or not state:
        return None
    qs = CountyLookup.objects.filter(
        county_nm=county_name, state_id=state, country_cd=country)
    if len(qs) == 0:
        return None
    return qs[0]


def _validate_decimal(field_name, dec_value, row_index, warning_messages):
    try:
        return Decimal(dec_value)
    except Exception:
        warning_messages.append(
            (row_index, {field_name: "Invalid Value '" + dec_value + "'"}))
    return None


def _get_monitoring_location(row_index, row, user, warning_messages):
    """
    Parses the list of strings that represent a row in the bulk upload template, validates and
    returns a MonitoringLocation instance. Raises Validation_Error if the row can not be converted
    :list of strings row:
    :User user
    :return: MonitoringLocation
    """
    if len(row) < 39:
        raise ValidationError(
            {'file_error': 'Does not contain the correct number of columns'}, code='invalid file')

    local_aquifer_code = f' ({row[15]})' if row[15] else ''
    country = _get_lookup(CountryLookup, 'country_nm', row[16])
    state = _get_state_lookup(country, row[17])

    monitoring_location = MonitoringLocation(
        agency=_get_lookup(AgencyLookup, 'agency_cd', row[0]),
        site_no=row[1],
        site_name=row[2],
        dec_lat_va=_validate_decimal(
            'dec_lat_va', row[3], row_index, warning_messages),
        dec_long_va=_validate_decimal(
            'dec_long_va', row[4], row_index, warning_messages),
        horizontal_datum=_get_lookup(
            HorizontalDatumLookup, 'hdatum_cd', row[5]),
        horz_method=row[6],
        horz_acy=row[7],
        alt_va=_validate_decimal(
            'alt_va', row[8], row_index, warning_messages),
        altitude_units=_get_lookup(UnitsLookup, 'unit_desc', row[9]),
        altitude_datum=_get_lookup(AltitudeDatumLookup, 'adatum_cd', row[10]),
        alt_method=row[11],
        alt_acy=row[12],
        nat_aqfr=_get_lookup(NatAqfrLookup, 'nat_aqfr_cd', row[13]),
        local_aquifer_name=f'{row[14]}{local_aquifer_code}',
        country=country,
        state=state,
        county=_get_county_lookup(country, state, row[18]),
        well_depth=_validate_decimal(
            'well_depth', row[19], row_index, warning_messages),
        well_depth_units=_get_lookup(UnitsLookup, 'unit_desc', row[20]),
        site_type=row[21],
        aqfr_type=row[22],
        display_flag=row[23] == 'Yes',
        qw_sn_flag=row[24] == 'Yes',
        qw_baseline_flag=row[25] == 'Yes',
        qw_well_chars=row[26],
        qw_well_type=row[27],
        qw_well_purpose=row[28],
        qw_well_purpose_notes=row[29],
        qw_network_name=row[30],
        wl_sn_flag=row[31] == 'Yes',
        wl_baseline_flag=row[32] == 'Yes',
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
    """
    Form containing a single file field
    """
    file = FileField()


class BulkUploadView(View):
    """
    Bulk upload view containing a single file field.
    """
    form_class = BulkUploadForm
    template_name = 'admin/bulk_upload.html'

    def get(self, request):
        """
        Overrides View's get method, adding the form
        """
        context = {
            'form': self.form_class()
        }
        context.update(dict(admin.site.each_context(self.request)))
        return render(request, self.template_name, context)

    def post(self, request):
        """
        Overrides View''s post method, processing the file and displaying the errrors
        if any. Successful validation redirect back to the monitoring location
        """
        context = {
            'form': self.form_class()
        }
        if 'file' in request.FILES:
            csv_file = request.FILES['file']
            data_set = csv_file.read().decode('UTF-8')
            data_stream = io.StringIO(data_set)
            # Skip header
            next(data_stream)
            monitoring_locations = []
            error_messages = []
            warning_messages = []
            row_index = 1
            for row in csv.reader(data_stream):
                row_index += 1
                try:
                    monitoring_locations.append(_get_monitoring_location(
                        row_index, row, request.user, warning_messages))
                except ValidationError as error:
                    error_messages.append((row_index, error.message_dict))
            if len(error_messages) == 0:
                MonitoringLocation.objects.bulk_create(monitoring_locations)
                if len(warning_messages) == 0:
                    return redirect(reverse('admin:registry_monitoringlocation_changelist'))
                warning_messages.insert(
                    0, (0, {'__overall__': 'Data was loaded with the following warnings'}))
            context['errors'] = error_messages
            context['warnings'] = warning_messages
        else:
            context['file_error'] = 'Please select a file to upload'
        context.update(dict(admin.site.each_context(self.request)))
        return render(request, self.template_name, context)


class BulkUploadTemplateView(View):
    """
    View to serve the bulk upload template
    """

    def get(self, request):
        """
        Overides View's get procedure
        """
        with open(settings.BULK_UPLOAD_TEMPLATE_PATH, 'rb') as excel:
            data = excel.read()
        response = HttpResponse(
            data, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=well_registry_bulk_update_template.xlsx'
        return response
