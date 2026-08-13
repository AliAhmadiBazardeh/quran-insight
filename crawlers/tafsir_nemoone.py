from dataclasses import dataclass

from bs4 import BeautifulSoup

from .base import BaseCrawler


@dataclass(slots=True)
class ParsedTafsir:
    ayah_numbers: list[int]
    text: str


class TafsirMakaremCrawler(BaseCrawler):

    BASE_URL = "https://quran.makarem.ir"
    TAFSIR_URL = BASE_URL + "/fa/interpretation"

    def get_soup(self, surah_number: int, verse_number: int):
        response = self.get(
            self.TAFSIR_URL,
            params={
                "sura": surah_number,
                "verse": verse_number,
            },
        )

        return BeautifulSoup(response.text, "lxml")

    def clean_text(self, element):
        """
        Convert HTML content into readable plain text.
        """

        soup = BeautifulSoup(str(element), "lxml")

        for br in soup.find_all("br"):
            br.replace_with("\n")

        for hr in soup.find_all("hr"):
            hr.replace_with("\n")

        text = soup.get_text("\n")

        lines = [
            line.strip().replace("\xa0", " ")
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    def parse_interpretation(self, soup):
        container = soup.select_one("div.interpretation-text")

        if container is None:
            raise RuntimeError(
                "Interpretation container not found."
            )

        # Remove footnotes
        for node in container.select("h5"):
            node.decompose()

        # Remove separators
        for node in container.select("hr"):
            node.decompose()

        result = []

        for element in container.find_all(
            ["h3", "h6", "p"],
            recursive=False,
        ):
            text = self.clean_text(element)

            if not text:
                continue

            # Ignore separator paragraphs such as:
            # * * *
            if text.replace("*", "").strip() == "":
                continue

            result.append(text)

        return "\n".join(result).strip()

    def parse_page(self, soup, verse_number: int):
        text = self.parse_interpretation(soup)

        if not text:
            raise RuntimeError(
                f"Empty interpretation for verse {verse_number}"
            )

        return ParsedTafsir(
            ayah_numbers=[verse_number],
            text=text,
        )

    def crawl_ayah(
        self,
        surah,
        verse_number,
        tafsir_source,
        user,
        tafsir_service,
    ):
        try:
            soup = self.get_soup(
                surah_number=surah.number,
                verse_number=verse_number,
            )

            parsed = self.parse_page(
                soup=soup,
                verse_number=verse_number,
            )

            tafsir, created = tafsir_service.save_tafsir(
                surah=surah,
                parsed=parsed,
                tafsir_source=tafsir_source,
                user=user,
            )

            if created:
                self.logger.warning(
                    "Saved %s:%s",
                    surah.number,
                    verse_number,
                )
            else:
                self.logger.warning(
                    "Skipped %s:%s",
                    surah.number,
                    verse_number,
                )

        except Exception:
            self.logger.exception(
                "Error processing %s:%s",
                surah.number,
                verse_number,
            )

    def crawl_surah(
        self,
        surah,
        tafsir_source,
        user,
        tafsir_service,
    ):
        """
        Crawl all verses of a surah.
        """

        ayah_count = surah.total_verses

        self.logger.warning(
            "Surah %s (%s): %s verses",
            surah.number,
            surah.name_fa,
            ayah_count,
        )

        for verse_number in range(1, ayah_count + 1):
            self.crawl_ayah(
                surah=surah,
                verse_number=verse_number,
                tafsir_source=tafsir_source,
                user=user,
                tafsir_service=tafsir_service,
            )

    def crawl(
        self,
        user,
        tafsir_source,
        tafsir_service,
    ):
        from quran.models import Surah

        surahs = (
            Surah.objects
            .all()
            .order_by("number")
        )

        for surah in surahs:
            self.crawl_surah(
                surah=surah,
                tafsir_source=tafsir_source,
                user=user,
                tafsir_service=tafsir_service,
            )