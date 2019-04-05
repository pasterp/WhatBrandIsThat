"""images_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.views import serve

from images import views

urlpatterns = [
    url(r'img_searches/feedback/(?P<pk>\d+)', views.Feedback.as_view()),
    url(r'img_searches/(?P<pk>\d+)', views.ImgSearch.as_view()),                        # "GET" /img_searches/[id_requete]
    url(r'img_searches', views.ImgSearch.as_view())                                     # "POST" /img_searches

]

