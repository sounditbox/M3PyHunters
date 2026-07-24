from rest_framework import serializers


def agreed_to_terms(value):
    if not value:
        raise serializers.ValidationError("You must agree to the terms")
