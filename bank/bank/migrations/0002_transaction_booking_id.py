# Generated by Django 4.1.6 on 2023-05-12 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='booking_id',
            field=models.IntegerField(null=True),
        ),
    ]