# encoding=utf8

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from PDFUpload import settings

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

import zipfile
#from lxml import etree
#from StringIO import StringIO
from bs4 import BeautifulSoup as bsoup

import codecs
import json

reload(sys)  
sys.setdefaultencoding('utf8')

def randomword(length):
   return ''.join(random.choice(string.lowercase + string.uppercase + string.digits) for i in range(length))

# Create your views here.

def index(request):
    return render_to_response('index.html', locals())

def pdf(request, filename):
    pdf_name = filename
    return render_to_response('redirect.html', locals())

#def epub(request, pages, styles, filename):
def epub(request, filename):
    filename = filename
        #if epub extraction fails user will be alerted
        #if not unzip_epub(temp, filename, filename_noextension, rand_key):
            #return False

        #filename_w_key = '%s-%s' % (filename_noextension, rand_key)
        #full_path = 'upload/static/%s/%s' % (path, filename_w_key)
        #template_data = process_epub_html(full_path, filename_w_key)
        #if file structure not as expected user will be alerted
        #if not template_data:
            #return False
        #pages = template_data[0]
        #styles = template_data[1]
        #epub_data = {'pages': pages, 'styles': styles, 'filename': filename_w_key}
        
        #return epub_data
    #print epub_data
    #filename = epub_data['filename']
    #styles = epub_data['styles']
    #pages = epub_data['pages']
    return render_to_response('epub.html', locals())

def csvAsTable(request, filename):
    file_path = "%s/%s" % (settings.BASE_DIR + settings.STATIC_URL + 'drop-pdf', filename)

    with open(file_path) as f:
        lines = f.readlines()

    title = lines[0].encode('utf8').split("\",")
    content = lines[1:]

    for index in range(0, len(content)):
        content[index] = content[index].encode('utf8').split("\",")

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
        #if epub extraction fails user will be alerted
        if not unzip_epub(temp, filename, filename_noextension, rand_key):
            return False

        filename_w_key = '%s-%s' % (filename_noextension, rand_key)
        full_path = 'upload/static/%s/%s' % (path, filename_w_key)
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

def unzip_epub(path, filename, filename_noextension, rand_key):
    '''Unzip epub into directory of same name and randkey without epub extension'''
    try:
        zipfl = zipfile.ZipFile('%s/%s' % (path, filename), 'r')
        zipfl.extractall('%s/%s-%s' % (path, filename_noextension, rand_key))
        zipfl.close()
        return True
    except:
        return False

def rewrite_style_sheet(sheet):
    '''Prefix epub style sheet elements with viewport id.
    Overwrite existing style sheet.
    This is to avoid collision with display page styles'''
    out = ''
    viewport_id = '#epub-inner-viewport'
    ss = open(sheet, 'r')
    for line in ss:
        start_element = re.search('{', line)
        if start_element:
            new_line_els = []
            #some elements refs have multiple comma seperated elements
            elems = line.split('{')[0].strip().split(',')
            for el in elems:
                el = el.strip()
                #remove body tags...replace them with viewport id
                el = el.replace('body', '').replace(' ', '')
                if len(el) == 0:
                    new_line_els.append(viewport_id)
                else:
                    new_line_els.append('%s %s' % (viewport_id, el))
            if len(new_line_els) == 1:
                new_line = new_line_els[0] + ' {\n'
            else:
                new_line = ', '.join(new_line_els) + ' {\n'
            out += new_line
            continue
        else:
            out += line
    ss.close()
    ss = open(sheet, 'w')
    ss.write(out)
    ss.close()

def process_epub_html(full_path, filename_w_key):
    '''prepare html to be rendered in template'''
    #toc file specifies display order
    toc_file = get_epub_toc(full_path)
    if not toc_file:
        return False

    #some epubs contain html files in inner directory.
    #this appears to be directory containing toc file
    #find where toc file is and this directory will be inner path

    toc = toc_file[1]
    path_with_inner = toc_file[0]
    
    pages = parse_epub_toc(toc, path_with_inner)
    style_refs = []
    
    for file_name in os.listdir(path_with_inner):

        #get actual document html files only
        fs = file_name.split('.')
        if len(fs) < 2:
            continue

        file_path = '%s/%s' % (path_with_inner, file_name)
        #preface styles on css sheets with viewport to avoid conflict with view page styling
        if fs[1] == 'css':
            rewrite_style_sheet(file_path)
            continue

        if fs[-1] not in ['html', 'htm'] or fs[0] == 'toc':
            continue

        file_ = open(file_path)
        parse = bsoup(file_.read(), 'lxml')
        file_.close()
        
        #to begin with assume all pages have same stylesheets
        stylelinks = parse.find_all('link', rel='stylesheet')
        for s in stylelinks:
            style_path = '%s/%s' % (path_with_inner, s)
            if not style_path in style_refs:
                style_refs.append(style_path)

        #get body inner html. rewrite the existing html page with only that
        inner_body = parse.find('body')
        #replace image paths with full path
        for img in inner_body.find_all('img'):
            img['src'] = '%s/%s' % (path_with_inner, img['src'])

        inner_html = str(inner_body.renderContents())

        file_ = open(file_path, 'w')
        file_.write(inner_html)
        file_.close()

        return (pages, style_refs)

def get_epub_toc(full_path):
    '''
    Find toc.ncx XML file path. If it doesn't exist return None.
    Otherwise return tuple of (directory, directory/file) 
    '''
    for dir_, subdir, files in os.walk(full_path, topdown=True):
        for f in files:
            if f == 'toc.ncx':
                return (dir_, '%s/%s' % (dir_, f))
    return None


def parse_epub_toc(toc, path_with_inner):
    '''get document html pages in order'''
    pages = []
    xml = open(toc).read()
    parse = bsoup(xml, 'lxml')

    for i in parse.find_all('content'):
        pages.append('%s/%s' % (path_with_inner, i['src']))

    return pages

def ocr(request):
    temp = settings.BASE_DIR + settings.STATIC_URL + "drop-pdf"
    filename = request.GET["filename"]
    
    start = int(round(time.time() * 1000))
    os.system("pypdfocr " + temp + "/" + str(filename))
    end = int(round(time.time() * 1000))
    print "%.2gs" % (end-start)

    new_filename = filename.split(".pdf")[0] + "_ocr" + ".pdf"

    return HttpResponse(new_filename)
# pp

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
