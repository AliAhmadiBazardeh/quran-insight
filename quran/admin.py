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

@admin.register(TafsirSource)
class TafsirSourceAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Tafsir)
class TafsirAdmin(admin.ModelAdmin):
    list_display = ['get_ayah_list', 'tafsir_source', 'order_priority']
    search_fields = ['ayah_list__surah__name_fa', 'ayah_list__number', 'text']
    autocomplete_fields = ['ayah_list', 'tafsir_source']


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # کاربران غیر سوپریوزر فقط تفسیرهایی را ببینند که خودشان ایجاد کرده‌اند
        return qs.filter(created_by=request.user)

    def get_form(self, request, obj=None, **kwargs):
        """محدود کردن انتخاب‌های ayah_list به آیات سوره‌های مجاز کاربر"""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            # فیلد ayah_list یک ManyToManyField است
            # می‌خواهیم فقط آیاتی نمایش داده شوند که سوره‌شان در allowed_surah_list کاربر باشد
            allowed_surah_list = request.user.allowed_surah_list.all()
            if allowed_surah_list.exists():
                form.base_fields['ayah_list'].queryset = Ayah.objects.filter(
                    surah__in=allowed_surah_list
                )
            else:
                form.base_fields['ayah_list'].queryset = Ayah.objects.none()
        return form

    def has_add_permission(self, request):
        # کاربران غیر سوپریوزر اگر حداقل یک سوره مجاز داشته باشند می‌توانند تفسیر اضافه کنند
        if request.user.is_superuser:
            return True
        return request.user.allowed_surah_list.exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        # فقط خود کاربر بتواند تفسیر خود را ویرایش کند
        if obj is not None and obj.created_by == request.user:
            return True
        return False


    def get_ayah_list(self, obj):
        return ', '.join(str(ayah) for ayah in obj.ayah_list.all())
    get_ayah_list.short_description = 'آیات'
    