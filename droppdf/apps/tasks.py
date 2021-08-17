from celery import shared_task
import subprocess
import os
import time
import json
import shutil
import binascii

from hashlib import md5

from django.conf import settings

from pdfrw import PdfReader, PdfWriter

from apps.utils.api_aws import S3 
from apps.utils.files import save_temp_file, cleanup_temp_file, check_ocr_file_exists, randword

from apps.models import OCRUpload

class MaxProcessesExceededError(Exception):
    pass


class FileInProcessError(Exception):
    '''raised when file with identical hash is already being processed'''
    pass


@shared_task
def ocr_pdf(filename, parent_id, md5_hash, force_flag):
    if not os.path.exists('/tmp/ocr_clients'):
        os.makedirs('/tmp/ocr_clients')

    lockfile = os.path.join('/tmp/ocr_clients', md5_hash)

    try:
        #prevent too many heavy ocr processes from running at once
        current_process_count = len(os.listdir('/tmp/ocr_clients'))

        if current_process_count >= int(settings.MAX_SIM_OCR_PROCESSES):
            raise MaxProcessesExceededError()

        #add to current process count with file
        try:
            f = open(lockfile, 'x')
            f.close()
        except FileExistsError:
            raise FileInProcessError()

        input_path = os.path.join('/tmp', filename)

        #download file and save 
        s3 = S3(settings.AWS_OCR_BUCKET)

        file_obj = s3.download_fileobj_from_bucket(filename)
        #file_obj.save(input_path)
        with open (input_path, 'wb') as tmpfile:
            tmpfile.write(file_obj.getbuffer())
            
       
        basename = '.'.join(filename.split('.')[:-1])
        if force_flag:
            processed_filename = basename + '_ocr_force.pdf'
            force_flag = True
        else:
            processed_filename = basename + '_ocr.pdf'
            force_flag = False

        output_path = os.path.join('/tmp', processed_filename)

        if force_flag:
            f = '--force-ocr'

        else:
            f = ''

        cmd = '/usr/bin/ocrmypdf {} {} {}'.format(f, input_path, output_path)

        rslt = subprocess.check_output(cmd, shell=True)

        #save to s3 
        with open(output_path, 'rb') as file_:
            s3.save_to_bucket(processed_filename, file_)

            file_.seek(0)

            hash_ = md5(file_.read()).hexdigest()

        #record to db
        ref = OCRUpload(filename=processed_filename, md5_hash=hash_,
                is_original=False, is_forced=force_flag, parent_id=parent_id)

        ref.save()

        #remove from process count 
        os.remove(lockfile)

        cleanup_temp_file(filename)
        cleanup_temp_file(processed_filename)

    except Exception as e:
        try:
            os.remove(os.path.join('/tmp/ocr_clients', md5_hash))
            cleanup_temp_file(filename)
            cleanup_temp_file(processed_filename)
        except:
            pass

        raise e


@shared_task
def delete_refingerprint(base_dir):
    '''clean up fingerprinted files'''
    time.sleep(10 * 60)

    shutil.rmtree(base_dir)


@shared_task
def refingerprint_pdf(filename, directory, copy_count, suffix):
    try:

        base_dir = os.path.join('/tmp/', directory)

        base_file_path = os.path.join(base_dir, filename)

        #file size kb
        file_size = round(os.path.getsize(base_file_path) / 1024)

        content = PdfReader(base_file_path)

        if content.ID is None:
            file_id = 'No ID'
        else:
            file_id = str(content.ID[0]).replace('<', '').replace('>', '')\
                    .replace('(', '').replace(')', '')

        #bad file_ids can contain strange characters
        try:
            file_id.encode('utf-8').strip()
        except UnicodeDecodeError:
            file_id = 'Unreadable'

        processed_files = []

        for copy_index in range(copy_count):

            if suffix and suffix != '':
                save_filename = filename + '-' + suffix + '-' + str(copy_index + 1) + '.pdf'
            else:
                save_filename = filename + '-' + str(copy_index + 1) + '.pdf'

            file_path = os.path.join('/tmp', directory, save_filename)

            download_link = '/fingerprinter/download/%s?file=%s' % (directory, save_filename)

            content = PdfReader(base_file_path)

            #add some random meta data
            content.Info.randomMetaData = binascii.b2a_hex(os.urandom(20)).upper()

            _filename = filename.strip().encode('utf-8')

            #change id to random id
            md = md5(_filename)

            md.update(str(time.time()).encode('utf-8'))
            md.update(os.urandom(10))

            new_id = md.hexdigest().upper()

            #keep length 32
            new_id = new_id[0:32]

            while len(new_id) < 32:
                new_id += random.choice('0123456789ABCDEF')

            content.ID = [new_id, new_id]

            PdfWriter(file_path, trailer=content).write()

            copy_info = {'filename': save_filename,
                    'download_link': download_link, 'id': content.ID[0]}

            processed_files.append(copy_info)

        #save copy of info in file directory 
        out_file = open(os.path.join(base_dir, 'file_info.json'), 'w')

        file_info = {'filename': filename, 'size': file_size, 'id': file_id,
            'directory_name': directory, 'processed_files': processed_files}

        json.dump(file_info, out_file, indent=4)
      
        out_file.close()

        #delete generated files
        delete_refingerprint.delay(base_dir)

    except Exception as e:
        delete_refingerprint.delay(base_dir)

        raise(e)
