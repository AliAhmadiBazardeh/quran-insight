from django.contrib import admin
from .models import Surah, Ayah, Tafsir, TafsirSource

admin.site.register(Surah)
admin.site.register(Ayah)
admin.site.register(Tafsir)
admin.site.register(TafsirSource)
