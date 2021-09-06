from django.shortcuts import render


def panopto(request):
    url = request.GET.get('url')
    return render(request, 'panopto.html', {'url': url})
