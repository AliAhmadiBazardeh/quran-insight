from django import forms
from django.core.exceptions import ValidationError
from .models import Tafsir

class TafsirAdminForm(forms.ModelForm):
    class Meta:
        model = Tafsir
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        tafsir_source = cleaned_data.get('tafsir_source')
        ayah_list = cleaned_data.get('ayah_list')  # این یک QuerySet یا لیستی از آیات است

        if not tafsir_source or not ayah_list:
            return cleaned_data

        # بررسی برای هر آیهٔ انتخاب‌شده
        for ayah in ayah_list:
            conflicting = Tafsir.objects.filter(
                tafsir_source=tafsir_source,
                ayah_list=ayah
            )
            # اگر در حال ویرایش هستیم، خود این رکورد را حذف کنید
            if self.instance.pk:
                conflicting = conflicting.exclude(pk=self.instance.pk)

            if conflicting.exists():
                raise ValidationError(
                    f"آیهٔ «{ayah}» قبلاً با منبع «{tafsir_source.title}» تفسیر شده است. "
                    "امکان ثبت تفسیر تکراری از یک منبع برای یک آیه وجود ندارد."
                )

        return cleaned_data