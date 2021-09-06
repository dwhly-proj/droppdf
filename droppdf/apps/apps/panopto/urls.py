from django.urls import path

from .views import *

urlpatterns = [
    path('panopto/', panopto, name='panopto')
]
