
from django.shortcuts import render


def custom_404(request, exception):
    data = {}
    return render(request, 'geocontrib/error/custom_404.html', data)


def custom_403(request, exception):
    data = {}
    return render(request, 'geocontrib/error/custom_403.html', data)