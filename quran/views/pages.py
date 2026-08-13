from django.shortcuts import render


def index(request):
    return render(request, "quran/index.html")


def about_view(request):
    return render(request, "quran/about.html")


def support_view(request):
    return render(request, "quran/support.html")


def contact_view(request):
    return render(request, "quran/contact.html")