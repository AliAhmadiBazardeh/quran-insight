from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('api/search/', views.live_search, name='live_search'),  # API جستجو
    path('api/tafsir/', views.get_tafsir, name='get_tafsir'),
]