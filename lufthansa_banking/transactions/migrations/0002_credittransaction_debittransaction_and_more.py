# Generated by Django 5.1.2 on 2024-10-17 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditTransaction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('transactions.transaction',),
        ),
        migrations.CreateModel(
            name='DebitTransaction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('transactions.transaction',),
        ),
        migrations.CreateModel(
            name='TransferTransaction',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('transactions.transaction',),
        ),
    ]
