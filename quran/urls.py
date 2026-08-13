from django.urls import path
from quran.views import dashboard, pages, tafsir, search

urlpatterns = [
    path("", pages.index, name="index"),
    path('about/', pages.about_view, name='about'),
    path('support/', pages.support_view, name='support'),
    path('contact/', pages.contact_view, name='contact'),
    path('api/search/', search.live_search, name='live_search'),
    path('api/tafsir/', tafsir.get_tafsir, name='get_tafsir'),
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),

]