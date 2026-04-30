from django.db import models
from .helper import normalize_persian

class Surah(models.Model):
    """مدل سوره‌های قرآن"""
    name = models.CharField(max_length=100, verbose_name="نام سوره")
    second_name = models.CharField(max_length=100, blank=True, verbose_name="نام دوم")
    name_fa = models.CharField(max_length=100, blank=True, verbose_name="نام فارسی سوره")
    second_name_fa = models.CharField(max_length=100, blank=True, verbose_name="نام دوم فارسی")
    name_en = models.CharField(max_length=100, blank=True, verbose_name="نام لاتین سوره")
    number = models.PositiveSmallIntegerField(unique=True, verbose_name="شماره سوره")
    total_verses = models.PositiveSmallIntegerField(verbose_name="تعداد آیات")

    class Meta:
        ordering = ['number']
        verbose_name = "سوره"
        verbose_name_plural = "سوره‌ها"

    def __str__(self):
        return f"{self.number}. {self.name_fa}"

    def save(self, *args, **kwargs):
        self.name_fa = normalize_persian('surah',self.name)
        self.second_name_fa = normalize_persian('surah',self.second_name) if self.second_name else False
        super().save(*args, **kwargs)

class Ayah(models.Model):
    """مدل آیه‌های قرآن"""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs', verbose_name="سوره")
    number= models.PositiveSmallIntegerField(verbose_name="شماره آیه در سوره")
    text = models.TextField(verbose_name="متن کامل آیه (عربی)")
    text_fa = models.TextField(blank=True, verbose_name="متن کامل آیه (فارسی)")
    text_prefix = models.CharField(max_length=50, blank=True, verbose_name="۲۰ کاراکتر اول آیه (برای نمایش سریع)")

    class Meta:
        ordering = ['surah__number', 'number']
        unique_together = ['surah', 'number']  # ترکیب سوره + شماره آیه یکتا باشد
        verbose_name = "آیه"
        verbose_name_plural = "آیات"

    def __str__(self):
        return f"{self.surah.name_fa} - آیه {self.number}"

    def save(self, *args, **kwargs):
        """قبل از ذخیره، text_prefix را از ۲۰ کاراکتر اول text پر کن"""
        if self.text:
            self.text_prefix = self.text[:50]
        self.text_fa = normalize_persian('ayah',self.text)
        super().save(*args, **kwargs)


class Tafsir(models.Model):
    """مدل تفسیر آیه"""
    ayah_list = models.ManyToManyField(
        'Ayah',
        related_name='tafsir_list',
        verbose_name="آیات مرتبط"
    )
    tafsir_source = models.ForeignKey(
        'TafsirSource',
        on_delete=models.CASCADE,
        related_name='tafsirs',
        verbose_name="منبع تفسیر")
    text = models.TextField(verbose_name="متن تفسیر")
    order_priority = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="اولویت ترتیب نمایش"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ['order_priority']
        verbose_name = "تفسیر"
        verbose_name_plural = "تفاسیر"
        indexes = [
            models.Index(fields=['order_priority']),
        ]

    def __str__(self):
        ayah_list = ', '.join(str(ayah) for ayah in self.ayah_list.all())
        return f"تفسیر {self.tafsir_source} برای {ayah_list}"

class TafsirSource(models.Model):
    verbose_name = "منبع تفسیر"
    verbose_name_plural = "منابع تفسیر"

    title = models.CharField(max_length=100, verbose_name="عنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "منبع تفسیر"
        verbose_name_plural = "منابع تفسیر"
    def __str__(self):
        return f"{self.title}"