# Generated by Django 4.1.6 on 2023-05-12 17:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('account_id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=255, unique=True)),
                ('balance', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=3)),
                ('symbol', models.CharField(max_length=1)),
                ('exchange_rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('booking_id', models.CharField(max_length=255)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('transaction_amount', models.FloatField()),
                ('account_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='bank.account')),
                ('transaction_currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.currency')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='currency_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.currency'),
        ),
    ]
