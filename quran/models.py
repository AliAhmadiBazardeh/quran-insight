from django.db import models
from .helper import normalize_persian

class Surah(models.Model):
    """مدل سوره‌های قرآن"""
    name = models.CharField(max_length=100, verbose_name="نام سوره")
    second_name = models.CharField(max_length=100, blank=True, verbose_name="نام دوم")
    persian_name = models.CharField(max_length=100, blank=True, verbose_name="نام فارسی سوره")
    persian_second_name = models.CharField(max_length=100, blank=True, verbose_name="نام دوم فارسی")
    latin_name = models.CharField(max_length=100, blank=True, verbose_name="نام لاتین سوره")

    number = models.PositiveSmallIntegerField(unique=True, verbose_name="شماره سوره")
    total_verses = models.PositiveSmallIntegerField(verbose_name="تعداد آیات")

    class Meta:
        ordering = ['number']
        verbose_name = "سوره"
        verbose_name_plural = "سوره‌ها"

    def __str__(self):
        return f"{self.number}. {self.persian_name}"

    def save(self, *args, **kwargs):
        self.persian_name = normalize_persian(self.name)
        self.persian_second_name = normalize_persian(self.second_name) if self.second_name else False
        super().save(*args, **kwargs)

class Ayah(models.Model):
    """مدل آیه‌های قرآن"""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs', verbose_name="سوره")
    number= models.PositiveSmallIntegerField(verbose_name="شماره آیه در سوره")
    text = models.TextField(verbose_name="متن کامل آیه (عربی)")
    text_fa = models.TextField(blank=True, verbose_name="متن کامل آیه (عربی)")
    text_prefix = models.CharField(max_length=50, blank=True, verbose_name="۲۰ کاراکتر اول آیه (برای نمایش سریع)")

    class Meta:
        ordering = ['surah__number', 'number']
        unique_together = ['surah', 'number']  # ترکیب سوره + شماره آیه یکتا باشد
        verbose_name = "آیه"
        verbose_name_plural = "آیات"

    def __str__(self):
        return f"{self.surah.persian_name} - آیه {self.number}"

    def save(self, *args, **kwargs):
        """قبل از ذخیره، text_prefix را از ۲۰ کاراکتر اول text پر کن"""
        if self.text and not self.text_prefix:
            self.text_prefix = self.text[:20]
        self.text_fa = normalize_persian(self.text)
        super().save(*args, **kwargs)


class Tafsir(models.Model):
    """مدل تفسیر آیه"""
    ayah = models.ForeignKey(
        'Ayah',
        on_delete=models.CASCADE,
        related_name='tafsirs',
        verbose_name="آیه مرتبط"
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
            models.Index(fields=['ayah', 'order_priority']),
        ]

    def __str__(self):
        return f"تفسیر {self.tafsir_source.title} برای {self.ayah}"


class TafsirSource(models.Model):
    title = models.CharField(max_length=100, verbose_name="عنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    def __str__(self):
        return f"{self.title}"