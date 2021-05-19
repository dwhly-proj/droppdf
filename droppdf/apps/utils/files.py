import os
import re
import string
import random
import subprocess

from apps.models import FileUpload, OCRUpload

from hashlib import md5


def save_temp_file(new_filename, file_, subdir=None):
    '''Save file to disk in /tmp directory.
    returns tuple(md5 hash, temp file path)'''
    if subdir:
        tempfile_path = os.path.join('/tmp', subdir, new_filename)
    else:
        tempfile_path = os.path.join('/tmp', new_filename)

    hash_ = md5()

    fd = open(tempfile_path, 'wb')

    for chunk in file_.chunks():
        hash_.update(chunk)

        fd.write(chunk)

    fd.close()

    return (hash_.hexdigest(), tempfile_path)


def cleanup_temp_file(new_filename):
    '''Delete temp file from /tmp directory if exists'''
    try:
        tempfile_path = os.path.join('/tmp', new_filename)
        os.remove(tempfile_path)

    except (OSError, FileNotFoundError):
        pass


def check_file_exists(md5_hash):
    '''Check database for hash.
    Return filename if exists, otherwise False'''

    obj = FileUpload.objects.filter(md5_hash=md5_hash)

    if obj.exists():
        return obj.first().filename

    return False


def check_ocr_file_exists(md5_hash):
    '''Check database for hash.
    Return filename if exists, otherwise False'''

    obj = OCRUpload.objects.filter(md5_hash=md5_hash)

    if obj.exists():
        return obj.first().filename

    return False


def check_pdf_has_text(new_filename):
    '''Check if if pdf has text or is image pdf.
    Use cli tool "pdftotext" from poppler libs.

    An image pdf will usually show some "text" so discard very short results
    after replacing newlines and blank spaces etc. in first 1,000 or so chars'''
    try:
    
        cmd = 'pdftotext "/tmp/{0}" -'.format(new_filename)

        rslt = subprocess.check_output(cmd, shell=True)

        rslt = rslt[:1000].decode('utf-8', 'ignore')
        
        #remove whitespace, newlines etc.
        rslt = re.sub(r'\W', '', rslt)

        if len(rslt) < 3:
            return False

        return True

    except Exception as e:
        print('\n', e)
        return False


def file_record_db(md5_hash, filename):
    pass


def randword(length):
       return ''.join(random.choice(string.ascii_lowercase + string.digits)\
               for i in range(length))
