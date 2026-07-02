from bs4 import BeautifulSoup
from urllib.parse import urlencode
from .base import BaseCrawler
from dataclasses import dataclass


@dataclass(slots=True)
class ParsedTafsir:
    ayah_numbers: list[int]
    text: str

class TafsirNoorCrawler(BaseCrawler):

    # BASE_URL = "https://gharaati.ir/تفسیر-نور/"
    BASE_URL = "https://gharaati.ir"

    OPTIONS_URL = BASE_URL + "/mydata.php"

    TAFSIR_URL = BASE_URL + "/show3.php"

    def get_soup(self, surah_number: int, option_value: int):

        response = self.get(
            self.TAFSIR_URL,
            params={
                "page": "tafsir3",
                "numsooreh": surah_number,
                "numayeh": option_value,
            },
        )

        return BeautifulSoup(response.text, "lxml")

    def get_ayah_options(self, surah_number):

        response = self.get(
            self.OPTIONS_URL,
            params={
                "op": "getayehlist",
                "id": surah_number,
            },
        )

        soup = BeautifulSoup(response.text, "lxml")

        options = []

        for option in soup.select("option"):

            value = option.get("value")
            label = option.get_text(strip=True)

            if not value:
                continue

            options.append({
                "value": int(value),
                "label": label,
            })

        if not options:
            raise RuntimeError(
                f"No ayah options found for surah {surah_number}"
            )

        return options

    def parse_ayah_numbers(self, label: str) -> list[int]:
        """
        Examples
        --------
        "5"           -> [5]
        "6،7"         -> [6, 7]
        "6,7"         -> [6, 7]
        "1-4"         -> [1, 2, 3, 4]
        "2،4-6،9"     -> [2, 4, 5, 6, 9]
        "1 - 3"       -> [1, 2, 3]
        """

        if not label:
            return []

        # یکسان‌سازی ویرگول‌ها و فاصله‌ها
        label = (
            label.replace("،", ",")
            .replace(" ", "")
            .replace("−", "-")
            .replace("–", "-")
            .replace("—", "-")
        )

        result = []

        for part in label.split(","):

            if not part:
                continue

            if "-" in part:

                start, end = part.split("-", 1)

                start = int(start)
                end = int(end)

                if start <= end:
                    result.extend(range(start, end + 1))
                else:
                    # اگر احیاناً برعکس بود
                    result.extend(range(end, start + 1))

            else:
                result.append(int(part))

        # حذف تکراری‌ها و مرتب‌سازی
        return sorted(set(result))

    def clean_html(self, element):

        soup = BeautifulSoup(str(element), "lxml")

        for br in soup.find_all("br"):
            br.replace_with("\n")

        for hr in soup.find_all("hr"):
            hr.replace_with("\n\n")

        text = soup.get_text("\n")

        lines = [
            line.strip().replace("\xa0", " ")
            for line in text.splitlines()
            if line.strip()
        ]

        return "\n".join(lines)

    def normalize_title(self, title: str):

        title = (
            title.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", "") # حذف نیم‌فاصله
            .replace("‌", "")
            .strip()
        )

        mapping = {
            "نکته ها": "نکات",
            "نکتهها": "نکات",
            "نکات": "نکات",

            "پیام ها": "پیام‌ها",
            "پیامها": "پیام‌ها",
            "پیام‌ها": "پیام‌ها",

            "سیمای سوره": "سیمای سوره",
        }

        return mapping.get(title)

    def parse_sections(self, soup):

        sections = {}

        blocks = soup.select("td.tafsir_title")

        for block in blocks:

            title_node = block.select_one("span.post-title")
            body_node = block.select_one("td.tafsir")

            if title_node is None or body_node is None:
                continue

            title = self.normalize_title(
                title_node.get_text(strip=True)
            )

            if title is None:
                continue

            if title in sections:
                self.logger.warning(
                    "Duplicate section: %s",
                    title,
                )

            sections[title] = self.clean_html(body_node)

        return sections

    def build_tafsir_text(self, sections):

        order = (
            "نکات",
            "پیام‌ها",
            "سیمای سوره",
        )

        result = []

        for title in order:

            body = sections.get(title)

            if not body:
                continue

            result.append(title)
            result.append(body)
            result.append("")

        return "\n".join(result).strip()

    def parse_page(self, soup, ayah_label):

        sections = self.parse_sections(soup)

        return ParsedTafsir(
            ayah_numbers=self.parse_ayah_numbers(ayah_label),
            text=self.build_tafsir_text(sections),
        )

    def crawl_surah(
            self,
            surah,
            tafsir_source,
            user,
            tafsir_service,
    ):
        options = self.get_ayah_options(surah.number)

        self.logger.warning(
            "Surah %s (%s): %s tafsir(s)",
            surah.number,
            surah.name_fa,
            len(options),
        )

        for option in options:
            try:
                soup = self.get_soup(
                    surah.number,
                    option["value"],
                )

                parsed = self.parse_page(
                    soup,
                    option["label"],
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
                        option["label"],
                    )
                else:
                    self.logger.warning(
                        "Skipped %s:%s",
                        surah.number,
                        option["label"],
                    )
            except Exception:

                self.logger.exception(
                    "Error processing %s:%s",
                    surah.number,
                    option["label"],
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
