import re
import io
import os
import random
import hashlib
import time
import string
import json
import shutil
import binascii

from django.shortcuts import render

from django.http import JsonResponse, Http404, HttpResponse, \
        HttpResponseNotFound

from django_http_exceptions import HTTPExceptions

from django_celery_results.models import TaskResult

from sanitize_filename import sanitize

from apps.tasks import refingerprint_pdf

from apps.utils.files import save_temp_file, randword


def fingerprinter(request):
    return render(request, 'refingerprint.html')


def fingerprinter_upload(request):
    processed_files = []

    pdf_file = request.FILES.get('pdf-file')
    copy_count = request.POST.get('copy-count', 1)
    suffix = request.POST.get('file-suffix', '')

    try:
        copy_count = int(copy_count)
    except:
        copy_count = 1

    if pdf_file is not None:

        s = os.path.splitext(pdf_file.name)
        filename = s[0].replace("'", '').replace('"', '')
        extension = s[-1]

        if extension.lower() != '.pdf':
            raise HTTPExceptions.NOT_ACCEPTABLE #Error code 406

        #make save directory 
        rand_path = randword(9)
        save_path = os.path.join('/tmp/', rand_path)
        os.makedirs(save_path)

        filename = sanitize(filename)

        filename = filename.replace("'", '').replace('"', '')
        filename = re.sub(r"[\(,\),\s]+", "-", filename)

        save_temp_file(filename, pdf_file, subdir=rand_path)

        #trigger fingerprint task
        task_id = refingerprint_pdf.delay(filename, rand_path, copy_count, suffix)

        data = {'directory': rand_path, 'filename': filename, 'task_id': str(task_id)}

        return JsonResponse(data)

    else:
        raise Http404('file not provided')


def fingerprinter_check_complete(request):
    '''check if refingerprint task has completed'''

    task_id = request.POST.get('task_id')

    if not task_id:
        raise Http404()

    obj = TaskResult.objects.filter(task_id=task_id)

    if obj.exists():
        obj = obj.first()

        if obj.status == 'SUCCESS':
            response = {'status': obj.status}

        else:
            response = {'status': 'FAIL'}

    else:
        response = {'status': 'INCOMPLETE'}

    return JsonResponse(response)


def fingerprinter_result(request):
    directory = request.GET.get('dir') 

    if not directory:
        raise Http404()

    base_directory = os.path.join('/tmp', directory)

    if not os.path.exists(base_directory):
        raise Http404()

    file_info = os.path.join(base_directory, 'file_info.json')

    if not os.path.exists(file_info):
        raise Http404()

    with open(file_info, 'r') as j:
        data = json.loads(j.read())

    return render(request, 'refingerprint_results.html', data)


def fingerprinter_download(request, directory):
    file_name = request.GET.get("file")

    if not file_name:
        raise Http404()

    file_location = os.path.join('/tmp', directory, file_name)

    if not os.path.exists(file_location):
        raise Http404()

    try:
        with open(file_location, 'rb') as f:
           file_data = f.read()

        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

    except IOError:
        response = HttpResponseNotFound('<h1>File does not exist</h1>')

    return response


def fingerprinter_compressed(request, directory):
    directory_path = os.path.join('/tmp', directory)

    #remove original and json leaving only refingerprints
    for file_ in os.listdir(directory_path):
        ext = file_.split('.')[-1]
        if ext != 'pdf':
            os.remove(os.path.join(directory_path, file_))

    tmp_name = '/tmp/%s' % directory
    tmp_zip = tmp_name + '.zip'

    #create zipfile
    content = shutil.make_archive(tmp_name, 'zip', directory_path)

    try:
        with open(tmp_zip, 'rb') as f:
           file_data = f.read()

        response = HttpResponse(file_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % directory
        os.remove(tmp_zip)

    except IOError:
        response = HttpResponseNotFound('<h1>File does not exist</h1>')

    return response
