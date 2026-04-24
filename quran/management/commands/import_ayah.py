import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from quran.models import Surah, Ayah


class Command(BaseCommand):
    help = 'Import verses from surah_X.json files, skipping verse_0 (Bismillah)'

    def handle(self, *args, **options):
        base_dir = os.path.join(settings.BASE_DIR, 'static', 'data', 'ayat_surah')

        if not os.path.exists(base_dir):
            self.stderr.write(self.style.ERROR(f'Directory not found: {base_dir}'))
            return

        surah_list = Surah.objects.all().order_by('number')
        total_created = 0
        total_skipped = 0

        for surah in surah_list:
            file_name = f'surah_{surah.number}.json'
            file_path = os.path.join(base_dir, file_name)

            if not os.path.exists(file_path):
                self.stderr.write(self.style.WARNING(f'Missing: {file_path}'))
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            verses = data.get('verse', {})
            if not verses:
                self.stdout.write(self.style.WARNING(f'No verses in {file_name}'))
                continue

            # استخراج کلیدها و مرتب‌سازی بر اساس شماره
            verse_keys = [k for k in verses.keys() if k.startswith('verse_')]
            verse_keys.sort(key=lambda x: int(x.split('_')[1]))

            created_count = 0
            skipped_count = 0

            for key in verse_keys:
                verse_num = int(key.split('_')[1])
                if verse_num == 0:
                    # این همان بسم الله است – رد می‌شود
                    self.stdout.write(self.style.NOTICE(
                        f'Surah {surah.number}: skipping verse_0 (Bismillah)'
                    ))
                    skipped_count += 1
                    continue

                verse_text = verses[key].strip()
                # ایجاد آیه (اگر قبلاً نبود)
                obj, created = Ayah.objects.get_or_create(
                    surah=surah,
                    number=verse_num,  # شماره آیه از 1 شروع می‌شود
                    defaults={'text': verse_text}
                )
                if created:
                    created_count += 1
                # else:
                    # در صورت وجود، متن را به‌روز می‌کنیم (اختیاری)
                    # if obj.text != verse_text:
                    #     obj.text = verse_text
                    #     obj.save()
                    #     self.stdout.write(self.style.WARNING(
                    #         f'Updated ayah {verse_num} of surah {surah.number}'
                    #     ))

            total_created += created_count
            total_skipped += skipped_count
            self.stdout.write(self.style.SUCCESS(
                f'Surah {surah.number} ({surah.name}): {created_count} created, {skipped_count} skipped (verse_0)'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done: {total_created} verses imported, {total_skipped} Bismillah skipped.'
        ))