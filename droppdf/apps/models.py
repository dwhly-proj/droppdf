from django.db import models

class FileUpload(models.Model):
    '''Reference to cloud upload'''
    filename = models.CharField(max_length=200)

    md5_hash = models.CharField(max_length=100)

    extension = models.CharField(max_length=8)

    is_original = models.BooleanField(default=True)

    parent = models.ForeignKey('FileUpload', on_delete=models.CASCADE,
            null=True, default=None)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

    class Meta:
        db_table = 'apps_fileupload'


class OCRUpload(models.Model):
    '''Reference to cloud upload for pdf files to be/have been ocrd'''
    filename = models.CharField(max_length=200)

    md5_hash = models.CharField(max_length=100)

    is_original = models.BooleanField(default=True)

    parent = models.ForeignKey('OCRUpload', on_delete=models.CASCADE,
            null=True, default=None)

    is_forced = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename

    class Meta:
        db_table = 'apps_ocr_upload'


class VideoSubtitle(models.Model): 
    lang_list = models.CharField(max_length=1024)
    
    video_id = models.CharField(max_length=100)
    
    subtitle = models.JSONField()                                                                                    
    
    created = models.DateTimeField(auto_now=False, auto_now_add=True)                                                                  
    
    updated = models.DateTimeField(auto_now=True)                                                                                      

    def __str__(self):
        return self.video_id

    class Meta:
        db_table = 'apps_video_subtitle'


class VideoAccessLog(models.Model): 
    
    video_id = models.CharField(max_length=100)

    user_ip = models.CharField(max_length=100)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)                                                                  

    class Meta:
        db_table = 'apps_video_access_log'
