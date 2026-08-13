from django.db import transaction

from .form import TafsirAdminForm
from django.contrib import admin
from .models import Surah, Ayah, Tafsir, TafsirSource
from jdatetime import datetime as jdatetime
from quran.tasks import send_tafsir_notification_task


class TafsirAyahLinkInline(admin.TabularInline):
    """ارتباط بین تفسیر و آیه را نشان می‌دهد"""
    model = Tafsir.ayah_list.through   # مدل واسط خودکار ManyToMany
    extra = 1
    verbose_name = "تفسیر مرتبط"
    verbose_name_plural = "تفاسیر مرتبط"
    autocomplete_fields = ['tafsir']   # نام فیلد ارجاع به Tafsir در مدل واسط

class AyahInline(admin.TabularInline):  # یا admin.StackedInline
    model = Ayah
    extra = 0  # تعداد ردیف خالی اضافی (صفر برای نمایش فقط آیات موجود)
    fields = [ 'number','text_prefix', 'tafsir_sources']  # فیلدهایی که نمایش داده شوند
    readonly_fields = ['number', 'text_prefix', 'tafsir_sources'] # اگر text_prefix به صورت خودکار پر می‌شود
    ordering = ['number']  # مرتب‌سازی بر اساس شماره آیه

@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ['name_fa','number',  'total_verses']
    search_fields = ['name_fa', 'name', 'number']
    inlines = [AyahInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # کاربران غیر سوپریوزر فقط سوره‌های مجاز خود را ببینند
        if request.user.allowed_surah_list.exists():
            return qs.filter(id__in=request.user.allowed_surah_list.all())
        # اگر هیچ سوره‌ای مجاز نباشد، نتیجه خالی برگردان
        return qs.none()

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ['__str__','text_prefix','tafsir_sources']
    search_fields = ['surah__name_fa', 'number', 'text_fa']
    list_filter = ['surah']
    autocomplete_fields = ['surah']


    def get_search_results(self, request, queryset, search_term):
        """
        محدود کردن نتایج جستجو (Autocomplete) برای کاربران غیر سوپریوزر
        فقط آیات سوره‌های مجاز برگردانده شوند
        """
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if not request.user.is_superuser:
            allowed_surah_list = request.user.allowed_surah_list.all()
            if allowed_surah_list.exists():
                queryset = queryset.filter(surah__in=allowed_surah_list)
            else:
                queryset = queryset.none()
        return queryset, use_distinct

@admin.register(TafsirSource)
class TafsirSourceAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Tafsir)
class TafsirAdmin(admin.ModelAdmin):
    form = TafsirAdminForm

    list_display = ['get_ayah_list','tafsir_source', 'created_by','get_shamsi_date']
    search_fields = ['ayah_list__surah__name_fa', 'ayah_list__number', 'text']
    autocomplete_fields = ['ayah_list', 'tafsir_source']
    readonly_fields = ['created_by']

    def get_shamsi_date(self, obj):
        if obj.created_at:
            jalali_date = jdatetime.fromgregorian(datetime=obj.created_at)
            return jalali_date.strftime('%Y/%m/%d %H:%M')
        return '-'

    get_shamsi_date.short_description = 'تاریخ ایجاد'

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
            # محدود کردن queryset اولیه فیلد (برای جلوگیری از نمایش همه آیات در صورت عدم استفاده از autocomplete)
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

    def save_model(self, request, obj, form, change):
        """به‌طور خودکار created_by را هنگام ذخیره تنظیم کن"""
        if not change:   # فقط در هنگام ایجاد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        transaction.on_commit(
            lambda: send_tafsir_notification_task.delay(
                obj_id=form.instance.pk,
                user_id=request.user.pk,
                change=change,
            )
        )

    def get_ayah_list(self, obj):
        return ', '.join(str(ayah) for ayah in obj.ayah_list.all())
    get_ayah_list.short_description = 'آیات'
    