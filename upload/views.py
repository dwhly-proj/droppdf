# encoding=utf8

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template import RequestContext
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
    #print filename, page, 'ZZ'
    #print filename.split('/'), 'aAAr'
    #filename = filename
    
    #find html file if exists
    filepath = filename.split('/')
    if len(filepath) == 2:
        page = filepath[1]
        filename = filepath[0]
    else:
        page = None

    print filename, page, 'ZZ'

    basepath = 'upload/static/drop-pdf'

    toc_path = find_resource('%s/%s' % (basepath, filename), 'toc.json')

    with open(toc_path) as file_:
        config = json.load(file_)

    out = {
            'filename': filename,
            'pages': config['pages'],
            'styles': config['styles']
            }

    out['page'] = 'Error fetching resource'

    if page is None:
        #get content for first page
        out['page'] = read_epub_page(out['pages'][0]['ref'])

    else:
        #get content for page specified in url
        for p in config['pages']:
            if p['short_ref'] == page:
                out['page'] = read_epub_page(p['ref'])
                break

    return render_to_response('epub.html', out, context_instance=RequestContext(request))

def epub_resource(request):
    #since real subdirectory is unknown, get file name and find where it is.
    #read the resource and return it
    path = request.path.split('/')
    resource = path[-1]
    root_dir = 'upload/static/drop-pdf/%s' % path[2]

    response = find_read_resource(root_dir, resource)

    return HttpResponse(response)

def epub_page_change(request):
    '''Send back html snippet to replace book page.'''
    src = request.POST.get("page_src")
    html = read_epub_page(src)
    return HttpResponse(html)

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

def read_epub_page(page):
    return open(page, 'r').read() 

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

    toc = toc_file[1]
    path_with_inner = toc_file[0]
    
    pages = parse_epub_toc(toc, path_with_inner)
    style_refs = []
   
    #assumed html files would be in same directory as toc.ncx
    #this turned out not to be the case. thus...walk whole directory

    #for file_name in os.listdir(path_with_inner):

    for dir_, subdir, files in os.walk(full_path, topdown=True):
        #for subd in subdir:
        for file_name in files:

            #get actual document html files only
            fs = file_name.split('.')
            if len(fs) < 2:
                continue

            #file_path = '%s/%s' % (path_with_inner, file_name)
            file_path = '%s/%s' % (dir_, file_name)
            
            #preface styles on css sheets with viewport to avoid conflict with view page styling
            if fs[1] == 'css':
                rewrite_style_sheet(file_path)
                continue

            if fs[-1] not in ['html', 'htm'] or fs[0] in ['toc']:
                continue

            file_ = open(file_path)
            parse = bsoup(file_.read(), 'lxml')
            file_.close()
            
            #to begin with assume all pages have same stylesheets
            stylelinks = parse.find_all('link', rel='stylesheet')
            for s in stylelinks:
                #replace image paths with url path for urls.py
                css = s['href'].split('/')[-1]
                style_path = 'epub_resources/%s' % css 
                if not style_path in style_refs:
                    style_refs.append(style_path)

            #get body inner html. rewrite the existing html page with only that
            inner_body = parse.find('body')

            #replace image paths with url path for urls.py
            for img in inner_body.find_all('img'):
                #we can find it in view by walking directory
                img_file = img['src'].split('/')[-1]
                img['src'] = 'epub_resources/%s' % img_file 

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
    '''Get document html pages in order.
    Returns: list of dictionaries.
    '''

    pages = []

    #don't duplicate page finds
    found_pages = []

    #page refs not to include in index
    xml = open(toc).read()
    parse = bsoup(xml, 'xml')

    #TODO this can be consolidated
    for i in parse.find_all('pageTarget'):
        text = i.find('navLabel').find('text').string
        cont = i.find('content')['src']

        #some books have a hash after doc name
        cont = cont.split('#')[0]

        #exclude the page from index if any following terms contained in src
        include = True
        #excludes = ['table-of-contents', 'pressbooks']
        #for term in excludes:
            #if re.search(term, str(cont)):
                #include = False
                #break
        if include:
            ref = '%s/%s' % (path_with_inner, cont)
    
            #tack extra text on existing for pages with multiple text
            if ref in found_pages:
                for p in pages:
                    if p['ref'] == ref:
                        p['text'] += ', ' + text
                        continue
            else:
                pages.append({'text': text, 'ref': ref, 'short_ref': cont})
                found_pages.append(ref)


    #for i in parse.find_all('content'):
    for i in parse.find_all('navPoint'):
        text = i.find('navLabel').find('text').string
        cont = i.find('content')['src']

        #some books have a hash after doc name
        cont = cont.split('#')[0]

        #exclude the page from index if any following terms contained in src
        include = True
        #excludes = ['table-of-contents', 'pressbooks']
        #for term in excludes:
            #if re.search(term, str(cont)):
                #include = False
                #break
        if include:
            ref = '%s/%s' % (path_with_inner, cont)

            #tack extra text on existing for pages with multiple text
            if ref in found_pages:
                for p in pages:
                    if p['ref'] == ref:
                        p['text'] += ', ' + text
                        continue
            else:
                pages.append({'text': text, 'ref': ref, 'short_ref': cont})
                found_pages.append(ref)

    return pages

def find_resource(root, resource):
    '''Walks root path until resource is found. Returns file location'''
    for dir_, subdir, files in os.walk(root, topdown=True):
        for file_name in files:
            if file_name == resource:
                return '%s/%s' % (dir_, file_name)

def find_read_resource(root, resource):
    '''Returns a binary read.'''
    file_path = find_resource(root, resource)
    
    return open(file_path, 'rb').read()
    #for dir_, subdir, files in os.walk(root, topdown=True):
        #for file_name in files:
            #if file_name == resource:

                #file_path = '%s/%s' % (dir_, file_name)
                #return open(file_path, 'rb').read()

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
