from django.core.paginator import Paginator

from quran.selectors.surah import (
    get_dashboard_global_stats,
    get_surah_list_for_dashboard,
)
from quran.selectors.tafsir import get_tafsir_sources


DASHBOARD_PAGE_SIZE = 3

TAFSIR_SOURCE_COLORS = [
    "#5470c6",
    "#91cc75",
    "#fac858",
    "#ee6666",
    "#73c0de",
    "#3ba272",
    "#fc8452",
    "#9a60b4",
]


class DashboardService:
    def get_surah_list_page(self, page_number=1):
        surah_list = get_surah_list_for_dashboard()

        paginator = Paginator(
            surah_list,
            DASHBOARD_PAGE_SIZE,
        )

        return paginator.get_page(page_number)

    def build_context(self, page_obj):
        tafsir_sources = list(
            get_tafsir_sources()
        )

        global_stats = (
            get_dashboard_global_stats()
        )

        surah_list_stats = self.build_surah_list_stats(
            surah_list=page_obj.object_list,
            tafsir_sources=tafsir_sources,
        )

        return {
            "surah_list_stats": surah_list_stats,
            "page_obj": page_obj,
            "tafsir_sources": [
                {
                    "id": source.id,
                    "title": source.title,
                }
                for source in tafsir_sources
            ],
            "total_sources": len(tafsir_sources),
            "total_surah_list_count": global_stats[
                "total_surah_list"
            ],
            "total_verses_global": global_stats[
                "total_verses"
            ],
            "total_ayahs_with_tafsir_global": (
                global_stats[
                    "total_ayahs_with_tafsir"
                ]
            ),
        }

    def build_surah_list_stats(
        self,
        surah_list,
        tafsir_sources,
    ):
        return [
            self.build_surah_stats(
                surah=surah,
                tafsir_sources=tafsir_sources,
            )
            for surah in surah_list
        ]

    def build_surah_stats(
        self,
        surah,
        tafsir_sources,
    ):
        ayahs = list(surah.ayahs.all())

        ayahs_with_tafsir = set()

        source_ayah_map = {
            source.id: set()
            for source in tafsir_sources
        }

        for ayah in ayahs:
            tafsirs = ayah.tafsir_list.all()

            if not tafsirs:
                continue

            ayahs_with_tafsir.add(ayah.id)

            for tafsir in tafsirs:
                source_ayah_map[
                    tafsir.tafsir_source_id
                ].add(ayah.id)

        total_ayahs_with_tafsir = len(
            ayahs_with_tafsir
        )

        verses_without_tafsir = (
            surah.total_verses
            - total_ayahs_with_tafsir
        )

        sources_stats = []

        for index, source in enumerate(
            tafsir_sources
        ):
            ayah_count = len(
                source_ayah_map[source.id]
            )

            if ayah_count == 0:
                continue

            sources_stats.append(
                {
                    "source_id": source.id,
                    "source_title": source.title,
                    "ayah_count": ayah_count,
                    "color": TAFSIR_SOURCE_COLORS[
                        index
                        % len(TAFSIR_SOURCE_COLORS)
                    ],
                }
            )

        completion_percentage = (
            total_ayahs_with_tafsir
            / surah.total_verses
            * 100
            if surah.total_verses > 0
            else 0
        )

        return {
            "surah_id": surah.id,
            "surah_name": surah.name_fa,
            "surah_number": surah.number,
            "total_verses": surah.total_verses,
            "verses_with_tafsir": (
                total_ayahs_with_tafsir
            ),
            "verses_without_tafsir": (
                verses_without_tafsir
            ),
            "completion_percentage": round(
                completion_percentage,
                2,
            ),
            "sources_stats": sources_stats,
        }


dashboard_service = DashboardService()