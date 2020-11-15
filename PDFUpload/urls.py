"""ChartApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from upload import views as upload_views
from pdf_annotator import views as annotator_views

urlpatterns = [
    url(r'^$', upload_views.index),
    url(r'^upload/', upload_views.upload, name="upload"),
    url(r'^drop/', upload_views.drop, name="drop"),
    url(r'^pdf/(?P<filename>.+\.pdf)/$', upload_views.pdf, name="pdf"),
    url(r'^ocr_dummy/$', upload_views.ocr, name="ocr"),
    url(r'^ocr/$', upload_views.ocr_pdf, name="ocr_pdf"),
    #url(r'^ocr/upload_and_check$', upload_views.ocr_upload_and_check,
        #name="ocr_upload_and_check"),
    url(r'^ocr/result/$', upload_views.ocr_pdf_result, name="ocr_pdf_result"),
    url(r'^ocr_pdf_complete$', upload_views.ocr_pdf_complete, name="ocr_pdf_complete"),
    url(r'^fingerprinter/$', upload_views.fingerprinter, name="fingerprinter"),
    url(r'^fingerprinter/upload/$', upload_views.fingerprinter_upload,
        name="refingerprint_upload"),
    url(r'^fingerprinter/download/(?P<directory_name>.+)/(?P<filename>.+)/$',
        upload_views.fingerprinter_download, name="fingerprinter_download"),
    url(r'^fingerprinter/compressed/(?P<directory_name>.+)/',
        upload_views.fingerprinter_compressed, name='fingerprinter_compressed'),
    url(r'^csv/(?P<filename>.+)/$', upload_views.csvAsTable, name="csv"),
    url(r'^epub/(?P<filename>.+)/$', upload_views.epub, name="epub"),
    url(r'video/(?P<video_id>.+)/$', upload_views.youtube_video, name='youtube_video'),
    url(r'pdf_annotator/', annotator_views.pdf_annotate, name='pdf_annotator')
]
