from django.urls import path, re_path

from .views import *

urlpatterns = [
        path('fingerprinter/', fingerprinter, name='fingerprinter'),
        path('fingerprinter/upload/', fingerprinter_upload, name='fingerprinter_upload'),
        path('fingerprinter/check_complete/', fingerprinter_check_complete, name='fingerprinter_check_complete'),
        path('fingerprinter/result/', fingerprinter_result, name='fingerprinter_result'),
        path('fingerprinter/download/<directory>', fingerprinter_download, name='fingerprinter_download'),
        path('fingerprinter/compressed/<directory>', fingerprinter_compressed, name='fingerprinter_compressed'),
        ]
