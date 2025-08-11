from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    """ Display the home page """
    return render(request, 'index.html')
