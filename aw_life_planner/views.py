from django.shortcuts import render


def index(request):
    """ Display the home page """
    return render(request, 'index.html')
