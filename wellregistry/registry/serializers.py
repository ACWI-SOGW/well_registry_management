"""
Serializers for the REST API
"""

from rest_framework.serializers import ModelSerializer, StringRelatedField

from .models import AgencyLookup, CountryLookup, CountyLookup, NatAqfrLookup, Registry, StateLookup


class AgencyLookupSerializer(ModelSerializer):
    class Meta:
        model = AgencyLookup
        exclude = ['id']

class NatAqfrLookupSerializer(ModelSerializer):
    class Meta:
        model = NatAqfrLookup
        exclude = ['id']

class CountryLookupSerializer(ModelSerializer):
    class Meta:
        model = CountryLookup
        fields = ['country_cd', 'country_nm']

class StateLookupSerializer(ModelSerializer):
    class Meta:
        model = StateLookup
        fields = ['state_cd', 'state_nm']

class CountyLookupSerializer(ModelSerializer):
    class Meta:
        model = CountyLookup
        fields = ['county_cd', 'county_nm']

class RegistrySerializer(ModelSerializer):
    agency = AgencyLookupSerializer()
    country = CountryLookupSerializer()
    state = StateLookupSerializer()
    county = CountyLookupSerializer()
    altitude_units = StringRelatedField()
    well_depth_units = StringRelatedField()
    nat_aqfr = NatAqfrLookupSerializer()

    class Meta:
        model = Registry
        exclude = ['insert_user', 'update_user']