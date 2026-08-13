from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from crawlers.tafsir_nemoone import TafsirMakaremCrawler
from quran.models import Surah, TafsirSource
from quran.services.tafsir import TafsirService


class Command(BaseCommand):
    help = "Crawl Tafsir Nemuneh from Makarem website"

    def add_arguments(self, parser):
        parser.add_argument(
            "--surah",
            default="all",
            help="Surah number (1-114) or 'all'",
        )

        parser.add_argument(
            "--user",
            type=int,
            required=True,
            help="User ID used as created_by",
        )

        parser.add_argument(
            "--source-id",
            type=int,
            required=True,
            help="TafsirSource ID",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(pk=options["user"])
        except User.DoesNotExist:
            raise CommandError("User not found.")

        try:
            tafsir_source = TafsirSource.objects.get(
                pk=options["source_id"]
            )
        except TafsirSource.DoesNotExist:
            raise CommandError("Tafsir source not found.")

        surah_option = options["surah"]

        if surah_option == "all":
            surahs = Surah.objects.order_by("number")

        else:
            try:
                surah_number = int(surah_option)
            except ValueError:
                raise CommandError(
                    "--surah must be an integer between 1 and 114 or 'all'."
                )

            if not 1 <= surah_number <= 114:
                raise CommandError(
                    "--surah must be between 1 and 114."
                )

            surahs = Surah.objects.filter(
                number=surah_number
            )

            if not surahs.exists():
                raise CommandError(
                    f"Surah {surah_number} does not exist."
                )

        crawler = TafsirMakaremCrawler()
        service = TafsirService()

        for surah in surahs:
            crawler.crawl_surah(
                surah=surah,
                tafsir_source=tafsir_source,
                user=user,
                tafsir_service=service,
            )