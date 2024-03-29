from django.urls import path

from .views import *

urlpatterns = [
        path('', view=home, name='home'),

        path('upload/', view=upload, name="upload"),

        path('pdf/<filename>/', view=pdf, name="pdf"),

        path('csv/<filename>/', view=csv_view, name="csv"),

        path('epub/<filename>/', view=epub, name="epub"),

        path('privacy/', view=privacy, name="privacy"),

        path('download/drop-pdf/<filename>', view=download_static,
            name="download_static"),

        path('download_annotation_doc/<filename>', view=download_static,
            name="download_annotation_doc"),

        path('handle_gdrive_doc', view=handle_gdrive_doc, name='handle_gdrive_doc'),

        path('process_gdrive_request', view=process_gdrive_request,
            name='process_gdrive_request')

        ]
