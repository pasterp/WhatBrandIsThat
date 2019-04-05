# Create your models here.
from django.db import models


"""class ImagesLook(models.Model):

    name=models.CharField(max_length=100, blank=True, default="")
    base64=models.CharField(max_length=2000001,blank=True, default="")
    url=models.CharField(max_length=100, blank=True, default="")
    description=models.CharField(max_length=100, blank=True, default="")
"""


class Request(models.Model):

    request_date=models.CharField(max_length=100, blank=True, default="")
    client=models.CharField(max_length=1000, blank=True, default="")
    base64=models.CharField(max_length=2000001,blank=True, default="")                      # max_length a modifier selon la longueur de la string en b64


class UrlResponse(models.Model):

    image_url=models.CharField(max_length=200, blank=True, default="")
    score=models.DecimalField(decimal_places=2,max_digits=4)

