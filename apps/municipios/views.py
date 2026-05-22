from django.shortcuts import render


def inicio(request):
    return render(request, "municipios/inicio.html")


def metodologia(request):
    return render(request, "municipios/metodologia.html")


def landing(request):
    return render(request, "municipios/landing.html")
