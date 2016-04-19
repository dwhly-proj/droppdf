from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from PDFUpload import settings
import os
import random, string
import re
import time

def randomword(length):
   return ''.join(random.choice(string.lowercase + string.uppercase + string.digits) for i in range(length))

# Create your views here.

def index(request):
	return render_to_response('index.html', locals())

def pdf(request, filename):
    pdf_name = filename
    return render_to_response('redirect.html', locals())


@csrf_exempt
def upload(request):
    filename = ""
    if request.method == 'POST':
        filename = save_file(request.FILES['file'], 'drop-pdf')
    return HttpResponse(filename)

def drop(request):
    if 'filename' in request.GET:
        file_path = "%s/%s" % (settings.BASE_DIR + settings.STATIC_URL + 'drop-pdf', request.GET['filename'])
        os.remove(file_path)

    return HttpResponse("")

# save uploaded pdf file and determine whether pdf has text or not.
#	return true-0-<filename> if pdf has text.
#	return false-<pagenum>-<filename>	if pdf has no text and must be ocred.
def save_file(file, path=''):
	temp = settings.BASE_DIR + settings.STATIC_URL + str(path)

	if not os.path.exists(temp):
		os.makedirs(temp)

	filename = file._get_name()
	filename = re.sub(r"\s+", "-", filename)

	filename_noextension = '.'.join(filename.split('.')[:-1])
	rand_key = randomword(5)

	filename = filename_noextension + "-" + rand_key + '.pdf'
	
	fd = open('%s/%s' % (temp, str(filename)), 'wb')
	for chunk in file.chunks():
		fd.write(chunk)
	fd.close()

	# get total number of pages 
	page_num = count_pages('%s/%s' % (temp, str(filename)))
	
	# check if pdf has text.
	os.system("pdftotext " + temp + "/" + str(filename))
	file_text = filename_noextension + "-" + rand_key + '.txt'
	
	with open(temp + "/" + file_text, 'rb') as f:
		str_data = f.read()
	os.remove(temp + "/" + file_text)

	if len(str_data) < page_num + 10:
		return 'false-' + str(page_num) + "-" + filename
	return 'true-0-' + filename

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


