from django.core.management.base import BaseCommand, CommandError

from quran.models import Surah, TafsirSource
from crawlers.tafsir_noor import TafsirNoorCrawler
from services.tafsir_service import TafsirService
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Crawl Tafsir Noor"

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

    def handle(self, *args, **options):
        User = get_user_model()

        try:
            user = User.objects.get(pk=options["user"])
        except User.DoesNotExist:
            raise CommandError("User not found.")

        surah = options["surah"]

        if surah == "all":
            surahs = Surah.objects.order_by("number")
        else:
            try:
                surah_number = int(surah)
            except ValueError:
                raise CommandError(
                    "--surah must be an integer between 1 and 114 or 'all'."
                )

            surahs = Surah.objects.filter(number=surah_number)

            if not surahs.exists():
                raise CommandError(
                    f"Surah {surah_number} does not exist."
                )

        crawler = TafsirNoorCrawler()
        service = TafsirService()
        tafsir_source = TafsirSource.objects.get(id=1)

        for surah in surahs:
            crawler.crawl_surah(
                surah=surah,
                tafsir_source=tafsir_source,
                user=user,
                tafsir_service=service,
            )