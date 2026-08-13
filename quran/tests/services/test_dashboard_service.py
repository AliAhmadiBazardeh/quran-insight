from django.test import TestCase
from quran.services.dashboard import dashboard_service
from quran.models import Ayah, Surah, Tafsir, TafsirSource

class DashboardServiceTests(TestCase):

    def test_get_surah_list_page_returns_paginated_surah_list(self):
        Surah.objects.create(
            number=1,
            name_fa="الفاتحه",
            total_verses=7,
        )
        Surah.objects.create(
            number=2,
            name_fa="البقره",
            total_verses=286,
        )
        Surah.objects.create(
            number=3,
            name_fa="آل عمران",
            total_verses=200,
        )
        Surah.objects.create(
            number=4,
            name_fa="النساء",
            total_verses=176,
        )

        page = dashboard_service.get_surah_list_page(
            page_number=1,
        )

        self.assertEqual(page.number, 1)
        self.assertEqual(page.paginator.num_pages, 2)
        self.assertEqual(len(page.object_list), 3)

        self.assertEqual(
            page.object_list[0].number,
            1,
        )
        self.assertEqual(
            page.object_list[2].number,
            3,
        )

    def test_get_surah_list_page_returns_second_page(self):
        for number in range(1, 5):
            Surah.objects.create(
                number=number,
                name_fa=f"سوره {number}",
                total_verses=10,
            )

        page = dashboard_service.get_surah_list_page(
            page_number=2,
        )

        self.assertEqual(page.number, 2)
        self.assertEqual(len(page.object_list), 1)
        self.assertEqual(
            page.object_list[0].number,
            4,
        )

    def test_build_surah_stats_calculates_tafsir_completion(self):
        surah = Surah.objects.create(
            number=1,
            name_fa="الفاتحه",
            total_verses=3,
        )

        source = TafsirSource.objects.create(
            title="تفسیر تست",
            order_priority=1,
        )

        ayah_1 = Ayah.objects.create(
            surah=surah,
            number=1,
            text="آیه اول",
        )

        ayah_2 = Ayah.objects.create(
            surah=surah,
            number=2,
            text="آیه دوم",
        )

        ayah_3 = Ayah.objects.create(
            surah=surah,
            number=3,
            text="آیه سوم",
        )

        tafsir = Tafsir.objects.create(
            tafsir_source=source,
            text="تفسیر آیه",
        )

        tafsir.ayah_list.add(
            ayah_1,
            ayah_2,
        )

        result = dashboard_service.build_surah_stats(
            surah=surah,
            tafsir_sources=[source],
        )

        self.assertEqual(
            result["total_verses"],
            3,
        )

        self.assertEqual(
            result["verses_with_tafsir"],
            2,
        )

        self.assertEqual(
            result["verses_without_tafsir"],
            1,
        )

        self.assertEqual(
            result["completion_percentage"],
            66.67,
        )

    def test_build_surah_list_stats_returns_stats_for_each_surah(self):
        surah_1 = Surah.objects.create(
            number=1,
            name_fa="الفاتحه",
            total_verses=7,
        )

        surah_2 = Surah.objects.create(
            number=2,
            name_fa="البقره",
            total_verses=286,
        )

        result = dashboard_service.build_surah_list_stats(
            surah_list=[surah_1, surah_2],
            tafsir_sources=[],
        )

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0]["surah_id"],
            surah_1.id,
        )

        self.assertEqual(
            result[1]["surah_id"],
            surah_2.id,
        )