from django.core.management.base import BaseCommand
from faker import Faker
from datetime import datetime

from patient_view.models import Patient, VitalSign

faker = Faker()


class Command(BaseCommand):
    help = "Creates fake patients and vital signs"

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, n, *args, **options):
        Patient.objects.all().delete()  # deletes all old patients and vital signs

        for i in range(n):
            patient = Patient.objects.create(
                # meta
                food_cosher=faker.boolean(),
                food_diary_restricted=faker.boolean(),
                # patient
                first_name=faker.first_name(),
                last_name=faker.last_name(),
                patient_id=faker.random_number(digits=9),
                description=faker.text(),
                birth_date=faker.date_of_birth(),
            )

            # Generate fake VitalSign records for each patient
            for _ in range(
                    faker.random_int(min=1, max=10)):  # You can adjust the number of VitalSign records per patient
                heart_rate = faker.random_int(min=60, max=100)
                spo2 = faker.random_int(min=90, max=100)

                VitalSign.objects.create(
                    patient=patient,
                    heart_rate=heart_rate,
                    spo2=spo2,
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully created {n} fake patients and vital signs.'))
