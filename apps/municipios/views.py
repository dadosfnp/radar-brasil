from django.shortcuts import render


def inicio(request):
    return render(request, "municipios/inicio.html")


def sobre(request):
    return render(request, "municipios/sobre.html")


def metodologia(request):
    return render(request, "municipios/metodologia.html")


def landing(request):
    return render(request, "municipios/landing.html")
