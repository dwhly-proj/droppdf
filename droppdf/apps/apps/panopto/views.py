import requests
from django.shortcuts import render, redirect

from django.http import StreamingHttpResponse


def panopto(request):
    url = request.GET.get('url')
    return render(request, 'panopto.html', {'url': url})


def panopto_proxy(request):
    url = request.GET.get('url')

    #print('XXXX', url)

    #response = requests.get(url, stream=True)

    #print(response.raw)

    #return StreamingHttpResponse(
        #response.raw,
        #content_type=response.headers.get('content-type'),
        #status=response.status_code,
        #reason=response.reason)
    return redirect(url)
