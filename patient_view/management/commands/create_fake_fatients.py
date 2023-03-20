from django.core.management.base import BaseCommand
from faker import Faker
from datetime import datetime

from patient_view.models import Patient

faker = Faker()


class Command(BaseCommand):
    help = "Creates fake patients"

    def add_arguments(self, parser):
        parser.add_argument('n', type=int)

    def handle(self, n, *args, **options):
        for i in range(n):
            first_name = faker.first_name()
            last_name = faker.last_name()
            full_name = f"{last_name} {first_name}"
            start_enter_date = datetime.strptime('30.11.1997', '%d.%m.%Y')
            end_enter_date = datetime.strptime('30.11.1998', '%d.%m.%Y')
            start_exit_date = datetime.strptime('10.12.1998', '%d.%m.%Y')
            end_exit_date = datetime.strptime('10.12.1999', '%d.%m.%Y')

            Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                full_name=full_name,
                id=faker.random_number(digits=9),
                enter_date=faker.date_between(start_date=start_enter_date, end_date=end_enter_date),
                leave_date=faker.date_between(start_date=start_exit_date, end_date=end_exit_date)
            )
