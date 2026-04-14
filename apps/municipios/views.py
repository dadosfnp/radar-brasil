from django.shortcuts import render

def landing(request):
    return render(request, "municipios/landing.html")

def inicio(request):
    return render(request, "municipios/inicio.html")