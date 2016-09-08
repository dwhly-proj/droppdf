from django.shortcuts import render
from django.shortcuts import render_to_response

#configs.py contains secrets that shouldn't be in the public repo
#so handle it if the file isn't there... don't prevent the whole app from running
try:
    from configs import CLIENT_ID, API_KEY, SCOPES  
except ImportError:
    CLIENT_ID = ''
    API_KEY = ''
    SCOPES = []

# Create your views here.

def pdf_annotate(request):
    return render_to_response('pdf_annotate.html', {
        'client_id': CLIENT_ID,
        'api_key': API_KEY,
        'scopes': SCOPES
        }
    )
