# Generated by Django 4.1.7 on 2023-03-15 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0004_appointmentlink_doctor_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentslot',
            name='patient_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
