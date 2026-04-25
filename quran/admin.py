from django.contrib import admin
from .models import Surah, Ayah, Tafsir, TafsirSource

from django.contrib import admin
from .models import Surah, Ayah, Tafsir, TafsirSource

class TafsirInline(admin.StackedInline):  # استفاده از Stacked برای متن طولانی تفسیر
    model = Tafsir
    extra = 1
    fields = ['tafsir_source', 'text', 'order_priority']
    autocomplete_fields = ['tafsir_source']

@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ['number', 'name_fa', 'total_verses']
    search_fields = ['name_fa', 'name', 'number']

@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'surah', 'number','text_prefix']
    search_fields = ['surah__name_fa', 'number', 'text_fa']
    list_filter = ['surah']
    autocomplete_fields = ['surah']
    inlines = [TafsirInline]

@admin.register(TafsirSource)
class TafsirSourceAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Tafsir)
class TafsirAdmin(admin.ModelAdmin):
    list_display = ['ayah', 'tafsir_source', 'order_priority']
    search_fields = ['ayah__surah__name_fa', 'ayah__number', 'text']
    autocomplete_fields = ['ayah', 'tafsir_source']