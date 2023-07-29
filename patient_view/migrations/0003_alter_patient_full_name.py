# Generated by Django 4.2.1 on 2023-07-29 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient_view', '0002_alter_patient_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='full_name',
            field=models.CharField(editable=False, help_text='Please do not edit or delete this. Your changes here will not be saved.', max_length=93),
        ),
    ]
