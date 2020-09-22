# encoding=utf8
import time
import os
import hashlib
import binascii
import io

from pdfrw import PdfReader, PdfWriter

from youtube_transcript_api import YouTubeTranscriptApi
import requests


from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.http import HttpResponse, Http404, JsonResponse
from django.template import RequestContext


from PDFUpload import settings

#configs.py contains secrets that shouldn't be in the public repo
#so handle it if the file isn't there... don't prevent the whole app from running
try:
    from pdf_annotator.configs import CLIENT_ID, API_KEY, SCOPES  
except ImportError:
    CLIENT_ID = ''
    API_KEY = ''
    SCOPES = []

import sys
import os
import random, string
import re
import time

import os.path
from textwrap import TextWrapper
from docx import opendocx, getdocumenttext
from xtopdf.PDFWriter import PDFWriter

import xlrd
import csv

import codecs
import json

reload(sys)  
sys.setdefaultencoding('utf8')

def randomword(length):
   return ''.join(random.choice(string.lowercase + string.uppercase + string.digits) for i in range(length))

# Create your views here.

def index(request):
    #for Google drive auth
    client_id = CLIENT_ID
    api_key = API_KEY
    scopes = SCOPES
    return render_to_response('index.html', locals())

def pdf(request, filename):
    pdf_name = filename
    return render_to_response('redirect.html', locals())

def epub(request, filename):
    return render_to_response('epub.html', locals())

def csvAsTable(request, filename):
    file_path = "%s/%s" % (settings.BASE_DIR + settings.STATIC_URL + 'drop-pdf', filename)

    with open(file_path, 'rU') as file_:
        reader = csv.reader(file_)
        title = reader.next()
        content = [i for i in reader]

    return render_to_response('table.html', locals())

@csrf_exempt
def upload(request):
    filename = ""
    if request.method == 'POST':
        file = request.FILES['file']
        filename = file._get_name()
        
        temp = filename.split('.')
        extension = temp[len(temp) - 1]

        filename = save_file(request.FILES['file'], 'drop-pdf', extension)
            
    return HttpResponse(filename)

def drop(request):
    if 'filename' in request.GET:
        file_path = "%s/%s" % (settings.BASE_DIR + settings.STATIC_URL + 'drop-pdf', request.GET['filename'])
        os.remove(file_path)

    return HttpResponse("")

# save uploaded pdf file and determine whether pdf has text or not.
#   return true-0-<filename> if pdf has text.
#   return false-<pagenum>-<filename>   if pdf has no text and must be ocred.
def save_file(file, path='', extension='pdf'):
    temp = settings.BASE_DIR + settings.STATIC_URL + str(path)

    if not os.path.exists(temp):
        os.makedirs(temp)

    filename = file._get_name()
    filename = filename.replace("'", '').replace('"', '')
    filename = re.sub(r"[\(,\),\s]+", "-", filename)

    filename_noextension = '.'.join(filename.split('.')[:-1])
    rand_key = randomword(5)

    filename = filename_noextension + "-" + rand_key + '.' + extension
    
    fd = open('%s/%s' % (temp, str(filename)), 'wb')
    for chunk in file.chunks():
        fd.write(chunk)
    fd.close()

    if extension == "pdf":
        # get total number of pages 
        page_num = count_pages('%s/%s' % (temp, str(filename)))
    
        # check if pdf has text.
        os.system("pdftotext " + temp + "/" + str(filename))
        file_text = filename_noextension + "-" + rand_key + '.txt'
    
        txt_path = temp + "/" + file_text

        if not os.path.exists(txt_path):

            print 'no text'
            return 'none-' + str(page_num) + "-" + filename
        with open(temp + "/" + file_text, 'rb') as f:
            str_data = f.read()
        os.remove(temp + "/" + file_text)

        if len(str_data) < page_num + 10:
            return 'false-' + str(page_num) + "-" + filename
        return 'true-0-' + filename
    elif extension == 'docx' or extension == 'doc':
        # convert docx to pdf
        pdf_name = filename_noextension + "-" + rand_key + '.pdf'
        pdf_path = '%s/%s' % (temp, str(pdf_name))
        docx_to_pdf('%s/%s' % (temp, str(filename)), pdf_path)

        return 'true-0-' + pdf_name
    elif extension == 'xlsx' or extension == 'xls':
        csv_name = filename_noextension + "-" + rand_key + '.csv'
        csv_path = '%s/%s' % (temp, str(csv_name))

        csv_from_excel('%s/%s' % (temp, str(filename)), csv_path)

        return csv_name
    elif extension == 'csv':
        return filename_noextension + "-" + rand_key + '.csv'

    elif extension == 'epub':
        return filename_noextension + "-" + rand_key + '.epub'


        #if epub extraction fails user will be alerted
        if not unzip_epub(temp, filename, filename_noextension, rand_key):
            return False

        filename_w_key = '%s-%s' % (filename_noextension, rand_key)
        full_path = os.path.join(settings.BASE_DIR, 'static', path, filename_w_key) 
        #full_path = 'upload/static/%s/%s' % (path, filename_w_key)
        template_data = process_epub_html(full_path, filename_w_key)
        #if file structure not as expected user will be alerted
        if not template_data:
            return False
        pages = template_data[0]
        styles = template_data[1]
        epub_data = {'pages': pages, 'styles': styles, 'filename': filename_w_key}

        #write a configuration file to be read when file url is requested
        #this data will be used to construct the template
        config_path = full_path + '/toc.json'
        with codecs.open(config_path, 'w', 'utf8') as f:
                 f.write(json.dumps(epub_data, sort_keys = True, ensure_ascii=False))

        return filename_w_key


def ocr(request):
    temp = settings.BASE_DIR + settings.STATIC_URL + "drop-pdf"
    filename = request.GET["filename"]
    
    start = int(round(time.time() * 1000))
    os.system("pypdfocr " + temp + "/" + str(filename))
    end = int(round(time.time() * 1000))
    print "%.2gs" % (end-start)

    new_filename = filename.split(".pdf")[0] + "_ocr" + ".pdf"

    return HttpResponse(new_filename)


def youtube_video(request, video_id):
    condensed_transcript = []

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except:
        return render_to_response('youtube_not_found.html', {})
        #raise Http404('<h1>Transcript not available for video or video not located.</h1>')

    subseconds = 0
    condensed_entry = None
    start_times = [];

    for entry in transcript:
        start = entry.get('start')
        text = entry.get('text', '')
        duration = entry.get('duration', 0)

        text = text.encode('utf-8', 'ignore')
        text = text.replace('\n', ' ')

        try:
            duration = float(duration)
        except:
            continue

        if condensed_entry is None:
            condensed_entry = {'start': start, 'text': text, 'duration': duration}

        else:
            condensed_entry['duration'] += duration
            condensed_entry['text'] += ' ' + text 

        if condensed_entry.get('duration', 0) > 23:
            condensed_entry['start_display'] = time.strftime('%H:%M:%S', 
                    time.gmtime(condensed_entry.get('start', 0))) 

            s = condensed_entry.get('start', 0)
            start_times.append(s)

            condensed_transcript.append(condensed_entry)
            subseconds = 0
            condensed_entry = None


    source = 'https://www.youtube.com/embed/'
    source += video_id
    source += '?enablejsapi=1'
    #source += '?enablejsapi=1&origin='
    #source += 'https://docdrop.org'
    source += '&widgetid=1'
    source += '&start=0&name=me'

    canonical_url = 'https://www.youtube.com/watch?v='
    canonical_url += video_id 

    noembed_url = 'https://noembed.com/embed?url=' + canonical_url 
    r = requests.get(noembed_url)

    title = ''
    if r.status_code == 200:
        try:
            video_info = r.json()
            if video_info:
                title = video_info.get('title')

        except:
            pass


    return render_to_response('youtube.html', {'transcript': condensed_transcript,
        'video_id': video_id, 'start_times': start_times, 'canonical_url': canonical_url, 
        'iframe_src': source, 'title': title})


def count_pages(filename):
    rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)
    data = file(filename,"rb").read()
    return len(rxcountpages.findall(data))


def docx_to_pdf(infilename, outfilename):
    # Extract the text from the DOCX file object infile and write it to 
    # a PDF file.

    #os.system("unoconv --listener")
    os.system("doc2pdf " + infilename)
    '''try:
        infil = opendocx(infilename)
    except Exception, e:
        print "Error opening infilename"
        print "Exception: " + repr(e) + "\n"
        sys.exit(1)

    paragraphs = getdocumenttext(infil)

    pw = PDFWriter(outfilename)
    pw.setFont("Courier", 12)
    #pw.setHeader("DOCXtoPDF - convert text in DOCX file to PDF")
    #pw.setFooter("Generated by xtopdf and python-docx")
    wrapper = TextWrapper(width=70, drop_whitespace=False)

    # For Unicode handling.
    new_paragraphs = []
    for paragraph in paragraphs:
        new_paragraphs.append(paragraph.encode("utf-8"))

    for paragraph in new_paragraphs:
        lines = wrapper.wrap(paragraph)
        for line in lines:
            pw.writeLine(line)
        pw.writeLine("")

    pw.savePage()
    pw.close()'''


def csv_from_excel(excel_file, csv_name):
    workbook = xlrd.open_workbook(excel_file)

    worksheet_name = workbook.sheet_names()[0]

    #all_worksheets = workbook.sheet_names()
    #for worksheet_name in all_worksheets:
    worksheet = workbook.sheet_by_name(worksheet_name)
    your_csv_file = open(csv_name, 'wb')
    wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in xrange(worksheet.nrows):
        wr.writerow([unicode(entry).encode("utf-8") for entry in worksheet.row_values(rownum)])
    your_csv_file.close()


#TODO CSRF token not working. need to fix this without breaking site, it may have
#been disabled by someone earlier but is important.
@ensure_csrf_cookie
def refingerprint(request):
    return render_to_response('refingerprint.html')


@csrf_exempt
def refingerprint_upload(request):
    pdf_file = request.FILES.get('pdf_file')
    copy_count = request.POST.get('copy_count', 1)

    try:
        copy_count = int(copy_count)
    except:
        copy_count = 1

    if pdf_file is not None:
        filename = pdf_file.name

        file_content = pdf_file.read()

        for copy_index in range(copy_count):
            content = PdfReader(io.BytesIO(file_content))

            #add some random meta data
            content.Info.randomMetaData = binascii.b2a_hex(os.urandom(20)).upper()

            #change id to random id
            md = hashlib.md5(filename)
            md.update(str(time.time()))
            md.update(os.urandom(10))

            content.ID = [md.hexdigest().upper(), md.hexdigest().upper()]

            PdfWriter("/tmp/edit.pdf", trailer=content).write()

    return JsonResponse({'result': 'ok'})
