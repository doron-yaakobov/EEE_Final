# Generated by Django 4.1.7 on 2023-03-20 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('first_name', models.CharField(max_length=46)),
                ('last_name', models.CharField(max_length=46)),
                ('full_name', models.CharField(max_length=92)),
                ('id', models.DecimalField(decimal_places=0, max_digits=9, primary_key=True, serialize=False)),
                ('enter_date', models.DateField()),
                ('leave_date', models.DateField()),
            ],
        ),
    ]