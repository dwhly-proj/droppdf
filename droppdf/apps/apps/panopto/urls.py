from django.urls import path

from .views import *

urlpatterns = [
    path('panopto/', panopto, name='panopto'),
    path('panopto_proxy/', panopto_proxy, name='panopto_proxy')
]
