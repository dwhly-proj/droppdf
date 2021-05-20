import re
import urllib
import os
#import subprocess
import csv
import time
import shutil

from sanitize_filename import sanitize

from django.shortcuts import render, redirect

from django.http import HttpResponse, Http404, JsonResponse, HttpResponseNotFound,\
        HttpResponseNotAllowed 

from django.core.exceptions import SuspiciousFileOperation, ValidationError

from django_http_exceptions import HTTPExceptions

from django.conf import settings

from apps.utils.api_aws import S3

from apps.utils.files import save_temp_file, cleanup_temp_file, check_file_exists,\
        check_pdf_has_text, randword 

from apps.models import FileUpload


def _soffice_process(tempfile_path, filename, md5_hash, process_type):
    '''create processed file,upload to s3, store ref'''

    #libre office requires invidual environs to run multiple instances
    #make empty file named to hash for unique we haz already.
    loffice_environ_path = os.path.join('/tmp', md5_hash)

    try:
        os.makedirs(loffice_environ_path)
    except FileExistsError:
        pass
    
    s = filename.split('.')
    child_name = '.'.join(s[:-1]) + '.' + process_type;
    extension = s[-1]

    outpath = os.path.join('/tmp', child_name)

    #t1 = time.time()

    try:
        os.system('/usr/bin/soffice -env:UserInstallation=file://%s \
            --headless --convert-to %s %s --outdir %s' \
            % (loffice_environ_path, process_type, tempfile_path, '/tmp'))
    except:
        raise HTTPExceptions.UNPROCESSABLE_ENTITY

    s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

    saved_file = open(outpath, 'rb')

    s3.save_to_bucket(child_name, saved_file)

    #save ref to db
    ref = FileUpload(filename=child_name, md5_hash=md5_hash,
            extension=extension, is_original=False)

    ref.save()

    cleanup_temp_file(child_name)
    cleanup_temp_file(filename)

    #remove environment file
    try:
        shutil.rmtree(loffice_environ_path)
    except:
        #shrug
        pass

    return child_name


def home(request):
    return render(request, 'index.html', {'request': request})


def upload(request):
    filename = ""
    if request.method == 'POST':
        file_ = request.FILES['file']

        filename = file_.name

        if not filename or len(filename) < 3 or not '.' in filename:
            raise SuspiciousFileOperation('improper file name')

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)

        temp = filename.split('.')
        basename = '.'.join(temp[:-1])
        extension = temp[-1]

        basename = basename[:60]

        new_filename = '{0}-{1}.{2}'.format(basename, randword(5), extension)

        #save file to disk temporarily.
        #later it will be deleted after uploading to s3.
        md5_hash, tempfile_path = save_temp_file(new_filename, file_)

        extension = extension.lower()

        #if file (or processed child) exists, return the name
        existing_name = check_file_exists(md5_hash)

        if existing_name:
            cleanup_temp_file(new_filename)

            return HttpResponse(existing_name)

        #transform process if needed
        process_to_file_type = False

        if extension in ['doc', 'docx', 'epub', 'odt', 'ott', 'rtf', 'odp', 'ppt', 'pptx']:
            process_to_file_type = 'pdf' 

        if extension in ['xls', 'xlsx', 'ods']:
            process_to_file_type = 'csv' 

        if process_to_file_type:
            child_name = _soffice_process(
                    tempfile_path, new_filename, md5_hash, process_to_file_type)

            if child_name:
                cleanup_temp_file(child_name)

                return HttpResponse(child_name)

            else:
                cleanup_temp_file(child_name)
                raise HTTPExceptions.UNPROCESSABLE_ENTITY


        if extension == 'pdf':
            #check if is an image pdf or if it has text
            if not check_pdf_has_text(new_filename):
                cleanup_temp_file(new_filename)
                raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406


        #upload to cloud
        s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

        saved_file = open(tempfile_path, 'rb')

        s3.save_to_bucket(new_filename, saved_file)

        #save ref to db
        ref = FileUpload(filename=new_filename, md5_hash=md5_hash,
                extension=extension, is_original=True)

        ref.save()

        cleanup_temp_file(new_filename)

        return HttpResponse(new_filename)

    return HttpResponseNotAllowed(['POST,'])


def pdf(request, filename):

    #file is in ocr bucket
    if request.GET.get('src') == 'ocr':
        s3 = S3(settings.AWS_OCR_BUCKET)

    else:
        s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

    url = s3.get_presigned_url(filename)

    return render(request, 'viewer.html', {'pdf_url': url})


def csv_view(request, filename):
    s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

    file_obj = s3.download_fileobj_from_bucket(filename)

    csv_data = file_obj.getvalue().decode('utf-8', 'ignore')

    reader = csv.reader(csv_data.splitlines())

    full_content = [i for i in reader]

    headers = full_content[0] 

    content = full_content[1:] 

    return render(request, 'csv_table.html', locals())


def epub(request, filename):
    s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

    url = s3.get_presigned_url(filename)

    return render(request, 'epub.html', {'book_url': url})


def privacy(request):
    return render(request, 'privacy.html')


def download_static(request, filename):
    '''to download documents from docdrop-v1 url format'''

    s3 = S3(settings.AWS_ANNOTATIONS_BUCKET)

    if s3.check_file_exists(filename): 
        url = s3.get_presigned_url(filename, expire=240000, content_type="application/pdf")

        return redirect(url)

    raise HTTPExceptions.NOT_FOUND
