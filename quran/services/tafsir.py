from django.db import transaction

from crawlers.tafsir_noor import ParsedTafsir
from quran.models import Ayah, Tafsir

class TafsirService:

    @transaction.atomic
    def save_tafsir(
            self,
            surah,
            parsed: ParsedTafsir,
            tafsir_source,
            user,
    ):
        """
            ذخیره یک تفسیر.

            Returns
            -------
            tuple[Tafsir, bool]
                (tafsir, created)

                created=True  => رکورد جدید ساخته شد.
                created=False => از قبل وجود داشت.
        """

        ayahs = list(
            Ayah.objects.filter(
                surah=surah,
                number__in=parsed.ayah_numbers,
            ).order_by("number")
        )

        if len(ayahs) != len(parsed.ayah_numbers):
            raise ValueError(
                f"Missing ayah(s) in Surah {surah.number}: "
                f"{parsed.ayah_numbers}"
            )

        ayah_ids = tuple(a.id for a in ayahs)

        existing = (
            Tafsir.objects
            .filter(
                tafsir_source=tafsir_source,
                ayah_list=ayahs[0],
            )
            .distinct()
        )

        for tafsir in existing:

            ids = tuple(
                tafsir.ayah_list
                .order_by("number")
                .values_list("id", flat=True)
            )

            if ids == ayah_ids:
                return tafsir, False

        tafsir = Tafsir.objects.create(
            tafsir_source=tafsir_source,
            text=parsed.text,
            created_by=user,
        )

        tafsir.ayah_list.set(ayahs)

        return tafsir, True