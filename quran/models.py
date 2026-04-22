from django.db import models

class Surah(models.Model):
    """مدل سوره‌های قرآن"""
    name = models.CharField(max_length=100, verbose_name="نام سوره")
    persian_name = models.CharField(max_length=100, verbose_name="نام فارسی سوره")
    latin_name = models.CharField(max_length=100, verbose_name="نام لاتین سوره")
    number = models.PositiveSmallIntegerField(unique=True, verbose_name="شماره سوره")
    total_verses = models.PositiveSmallIntegerField(verbose_name="تعداد آیات")

    class Meta:
        ordering = ['number']
        verbose_name = "سوره"
        verbose_name_plural = "سوره‌ها"

    def __str__(self):
        return f"{self.number}. {self.persian_name}"


class Ayah(models.Model):
    """مدل آیه‌های قرآن"""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs', verbose_name="سوره")
    number= models.PositiveSmallIntegerField(verbose_name="شماره آیه در سوره")
    text = models.TextField(verbose_name="متن کامل آیه (عربی)")
    text_prefix = models.CharField(max_length=50, blank=True, verbose_name="۲۰ کاراکتر اول آیه (برای نمایش سریع)")

    class Meta:
        ordering = ['surah__number', 'number']
        unique_together = ['surah', 'number']  # ترکیب سوره + شماره آیه یکتا باشد
        verbose_name = "آیه"
        verbose_name_plural = "آیات"

    def __str__(self):
        return f"{self.surah.name_fa} - آیه {self.number_in_surah}"

    def save(self, *args, **kwargs):
        """قبل از ذخیره، text_prefix را از ۲۰ کاراکتر اول text پر کن"""
        if self.text and not self.text_prefix:
            self.text_prefix = self.text[:20]
        super().save(*args, **kwargs)