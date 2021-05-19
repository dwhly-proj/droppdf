from django.contrib import admin

from .models import FileUpload, OCRUpload

admin.site.register(FileUpload)
admin.site.register(OCRUpload)
