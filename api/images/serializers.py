from rest_framework import serializers
from images.models import Request
from images.models import UrlResponse


class RequestSerializer(serializers.ModelSerializer):

    class Meta:

        model=Request
        fields = ('id','request_date','client','base64')                # les champs de la BdD


class UrlResponseSerializer(serializers.ModelSerializer):

    class Meta:

        model=UrlResponse
        fields=('url_id','request_id','image_url','score')              # le champs de la BdD


