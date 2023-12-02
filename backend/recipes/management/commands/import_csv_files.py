import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

TABLES = {
    Ingredient: 'ingredients.csv',
}


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            workdir = os.path.abspath(os.path.join(
                f'{settings.BASE_DIR}', './foodgram')
            )
            with open(
                    workdir + '/data/ingredients.csv',
                    newline='',
                    encoding='utf-8',
            ) as csv_file:
                reader = csv.DictReader(
                    csv_file,
                    fieldnames=['name', 'measurement_unit'],
                    delimiter=','
                )
                model.objects.bulk_create([model(**data) for data in reader])
        self.stdout.write(('Данные csv-файлов импортированы'))
