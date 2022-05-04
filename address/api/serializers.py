from drf_spectacular.utils import extend_schema_field
from parler_rest.fields import TranslatedFieldsField
from parler_rest.serializers import TranslatableModelSerializer
from rest_framework import serializers

from ..models import Address, Municipality, PostalCodeArea, Street
from .fields import LocationField


class TranslationsSerializer(serializers.Serializer):
    fi = serializers.CharField(required=False)
    sv = serializers.CharField(required=False)
    en = serializers.CharField(required=False)


@extend_schema_field(TranslationsSerializer)
class TranslationsField(TranslatedFieldsField):
    pass


class TranslatedModelSerializer(TranslatableModelSerializer):
    """
    A serializer that formats translated strings under language codes, e.g.

        {"fi": "Helsinki", "sv": "Helsingfors"}

    The serializer inheriting this should have "translations" listed in its fields.
    """

    translations = TranslationsField()

    def to_representation(self, obj):
        representation = super().to_representation(obj)
        translated_fields = {}
        for lang_key, trans_dict in representation.pop("translations", {}).items():
            for field_name, translation in trans_dict.items():
                if field_name not in translated_fields:
                    translated_fields[field_name] = {lang_key: translation}
                else:
                    translated_fields[field_name].update({lang_key: translation})
        representation.update(translated_fields)
        return representation


class MunicipalitySerializer(TranslatedModelSerializer):
    class Meta:
        model = Municipality
        fields = ["code", "translations"]


class StreetSerializer(TranslatedModelSerializer):
    class Meta:
        model = Street
        fields = [
            "translations",
        ]


class PostalCodeAreaSerializer(TranslatedModelSerializer):
    class Meta:
        model = PostalCodeArea
        fields = ["postal_code", "translations"]


class AddressSerializer(serializers.ModelSerializer):
    street = StreetSerializer()
    postal_code_area = PostalCodeAreaSerializer()
    location = LocationField()
    municipality = MunicipalitySerializer()

    class Meta:
        model = Address
        fields = [
            "street",
            "number",
            "number_end",
            "letter",
            "postal_code_area",
            "location",
            "modified_at",
            "municipality",
        ]
