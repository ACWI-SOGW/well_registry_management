"""
Serializers for the REST API
"""
# pylint: disable=too-few-public-methods

from rest_framework.serializers import ModelSerializer, StringRelatedField

from .models import AgencyLookup, CountryLookup, CountyLookup, NatAqfrLookup, MonitoringLocation, StateLookup, \
    UnitsLookup


class AgencyLookupSerializer(ModelSerializer):
    """
    Serializer for AgencyLookup
    """
    class Meta:
        model = AgencyLookup
        exclude = ['id']


class NatAqfrLookupSerializer(ModelSerializer):
    """
    Serializer for NatAqfrLookup
    """
    class Meta:
        model = NatAqfrLookup
        exclude = ['id']


class UnitsLookupSerializer(ModelSerializer):
    """
    Serializer for UnitsLookup
    """
    class Meta:
        model = UnitsLookup
        fields = ['unit_id', 'unit_desc']


class CountryLookupSerializer(ModelSerializer):
    """
    Serializer for CountryLookup
    """
    class Meta:
        model = CountryLookup
        fields = ['country_cd', 'country_nm']


class StateLookupSerializer(ModelSerializer):
    """
    Serializer for StateLookup
    """
    class Meta:
        model = StateLookup
        fields = ['state_cd', 'state_nm']


class CountyLookupSerializer(ModelSerializer):
    """
    Serializer for CountyLookup
    """
    class Meta:
        model = CountyLookup
        fields = ['county_cd', 'county_nm']


class MonitoringLocationSerializer(ModelSerializer):
    """
    Serializer for RegistrySerializer
    """
    agency = AgencyLookupSerializer()
    country = CountryLookupSerializer()
    state = StateLookupSerializer()
    county = CountyLookupSerializer()
    altitude_units = UnitsLookupSerializer()
    well_depth_units = UnitsLookupSerializer()
    nat_aqfr = NatAqfrLookupSerializer()
    insert_user = StringRelatedField()
    update_user = StringRelatedField()

    class Meta:
        model = MonitoringLocation
        fields = '__all__'
