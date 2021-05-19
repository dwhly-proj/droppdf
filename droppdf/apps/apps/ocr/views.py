import time
import re
import random
import json

from sanitize_filename import sanitize

from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from django.core.exceptions import SuspiciousFileOperation, ValidationError

from django.shortcuts import render, redirect

from django_http_exceptions import HTTPExceptions

from django.conf import settings

from django_celery_results.models import TaskResult

from apps.utils.api_aws import S3

from apps.utils.files import save_temp_file, cleanup_temp_file, check_ocr_file_exists,\
        randword, check_pdf_has_text

from apps.models import OCRUpload

from apps.tasks import ocr_pdf


def ocr(request):
    return render(request, 'ocr_pdf.html', {})


def upload(request):
    if request.method == 'POST':

        file_ = request.FILES.get('pdf-file')

        processing_error = None

        if file_ is None:
            raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        filename = file_.name

        if not filename or len(filename) < 3 or not '.' in filename:
            raise SuspiciousFileOperation('improper file name')

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)

        temp = filename.split('.')
        basename = '.'.join(temp[:-1])
        extension = temp[-1]

        if not extension in ('pdf', 'PDF'):
            raise SuspiciousFileOperation('improper file type')

        basename = basename[:60]

        new_filename = '{0}-{1}.{2}'.format(basename, randword(5), extension)

        #save to /tmp
        md5_hash, tempfile_path = save_temp_file(new_filename, file_)

        #file already exists in system?
        existing_name = check_ocr_file_exists(md5_hash)

        #already_has_text?
        if check_pdf_has_text(new_filename):
            processing_error = 'This PDF already has text. Use the "Force OCR" button to overwrite text with a fresh OCR if desired. If file was OCRd on previous upload those results will be provided'


        if not existing_name:
            already_exists = False

            #upload original to S3
            s3 = S3(settings.AWS_OCR_BUCKET)

            saved_file = open(tempfile_path, 'rb')

            s3.save_to_bucket(new_filename, saved_file)

            ref = OCRUpload(filename=new_filename, md5_hash=md5_hash, is_original=True)

            ref.save()

            cleanup_temp_file(new_filename)

        else:
            already_exists = True

            new_filename = existing_name

            cleanup_temp_file(new_filename)

        data = {'file_info': {'filename': filename, 'size': file_.size,
                    'new_filename': new_filename, 'processing_error': processing_error,
                    'tempfile_path': tempfile_path, 'already_exists': already_exists,
                    'md5_hash': md5_hash}}

        return JsonResponse(data)

    return HttpResponseNotAllowed(['POST,'])


def result(request):
    if request.method == 'POST':
        file_info = request.POST.get('file_info')

        force_flag = request.POST.get('force_flag')

        if not file_info:
            raise HTTPExceptions.BAD_REQUEST

        file_info = json.loads(file_info)

        md5_hash = file_info.get('md5_hash')
        new_filename = file_info.get('new_filename')

        processing_error = None

        #make sure parent file reference exists
        try:
            parent = OCRUpload.objects.filter(md5_hash=md5_hash)
            if parent.exists():
                parent = parent.first()
            else:
                raise HTTPExceptions.BAD_REQUEST

        except OCRUpload.DoesNotExist:
            raise HTTPExceptions.BAD_REQUEST

        if force_flag:
            child = OCRUpload.objects.filter(parent=parent, is_forced=True)
        else:
            child = OCRUpload.objects.filter(parent=parent, is_forced=False)

        #ocr has been performed already
        if child.exists():

            child = child.first()

            file_info['existing'] = True
            file_info['download_url'] = '/ocr/download/' + child.filename
            file_info['processed_filename'] = child.filename

        #trigger ocr
        else:
            task_id = ocr_pdf.delay(new_filename, parent.id, md5_hash, force_flag)

            basename = '.'.join(new_filename.split('.')[:-1])
            if force_flag:
                processed_filename = basename + '_ocr_force.pdf'
            else:
                processed_filename = basename + '_ocr.pdf'

            file_info['existing'] = False
            file_info['download_url'] = '/ocr/download/' + processed_filename 
            file_info['processed_filename'] = processed_filename
            file_info['task_id'] = str(task_id)


        data = {'file_info': file_info}

        data['json_file_info'] = json.dumps(file_info)

        return render(request, 'ocr_pdf_result.html', data)


    return HttpResponseNotAllowed(['POST,'])


def download(request, filename):
    s3 = S3(settings.AWS_OCR_BUCKET)

    if s3.check_file_exists(filename): 
        url = s3.get_presigned_url(filename)

        return redirect(url)

    raise HTTPExceptions.NOT_FOUND


def check_complete(request):
    #check if output file exists yet
    filename = request.POST.get('filename')
    task_id = request.POST.get('task_id')

    obj = TaskResult.objects.filter(task_id=task_id)

    if obj.exists():
        obj = obj.first()

        if obj.status == 'SUCCESS':
            s3 = S3(settings.AWS_OCR_BUCKET)

            download_url = s3.get_presigned_download_url(filename)

            response = {'status': obj.status, 'successful': True, 'download_url': download_url, 'error_detail': None}

        else:
            response = {'status': obj.status, 'successful': False, 'download_url': None, 'error_detail': obj.result}

        return JsonResponse(response)

    else:
        raise HTTPExceptions.NOT_FOUND
