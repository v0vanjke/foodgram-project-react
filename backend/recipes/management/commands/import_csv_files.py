import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient, Tag

TABLES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                    f'{settings.BASE_DIR}/static/data/{csv_f}', newline='',
                    encoding='utf-8'
            ) as csv_file:
                if csv_f == 'ingredients.csv':
                    reader = csv.DictReader(
                        csv_file,
                        fieldnames=['name', 'measurement_unit'],
                        delimiter=','
                    )
                    model.objects.bulk_create(
                        [model(**data) for data in reader]
                    )
                if csv_f == 'tags.csv':
                    reader = csv.DictReader(
                        csv_file,
                        fieldnames=['name', 'color', 'slug'],
                        delimiter=','
                    )
                    model.objects.bulk_create(
                        [model(**data) for data in reader]
                    )
        self.stdout.write(('Данные csv-файлов импортированы'))
