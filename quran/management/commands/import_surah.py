import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from quran.models import Surah


class Command(BaseCommand):
    help = 'Import surahs from surah_list.json into Surah model'

    def handle(self, *args, **options):

        json_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'surah_list.json')

        if not os.path.exists(json_path):
            self.stderr.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            surahs_data = json.load(f)

        created_count = 0
        updated_count = 0

        for item in surahs_data:
            # نگاشت فیلدها
            surah_number = item['id']
            surah_name = item['name']  # نام عربی
            surah_name_en = item.get('transliteration', '')
            total_verses = item['total_verses']

            obj, created = Surah.objects.update_or_create(
                id=surah_number,
                number=surah_number,
                defaults={
                    'name': surah_name,
                    'name_en': surah_name_en,
                    'total_verses': total_verses,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Import completed: {created_count} created, {updated_count} updated.'
        ))