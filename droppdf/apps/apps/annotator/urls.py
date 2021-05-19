from django.urls import path

from .views import *

urlpatterns = [
        path('', view=home, name='home'),

        path('upload/', view=upload, name="upload"),

        path('pdf/<filename>/', view=pdf, name="pdf"),

        path('csv/<filename>/', view=csv_view, name="csv"),

        path('epub/<filename>/', view=epub, name="epub"),

        path('privacy/', view=privacy, name="privacy"),

        path('static/drop-pdf/<filename>', view=download_static,
            name="download_static")
        ]
