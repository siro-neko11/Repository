# Generated by Django 4.1 on 2024-01-26 09:10

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'category',
            },
        ),
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'pament_type',
            },
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_name', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'vendor',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_date', models.DateField()),
                ('name_1', models.CharField(default='', max_length=20, null=True)),
                ('name_2', models.CharField(default='', max_length=20, null=True)),
                ('amount', models.IntegerField(default=0)),
                ('memo', models.TextField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='household_budget.category')),
                ('payment_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='household_budget.paymenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vendor_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_transactions', to='household_budget.vendor')),
            ],
            options={
                'db_table': 'BalanceOfPayments',
                'ordering': ['event_date'],
            },
        ),
        migrations.CreateModel(
            name='Goal_Saving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(default=django.utils.timezone.now)),
                ('savings_goal', models.IntegerField(null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'goal_saving',
            },
        ),
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_date', models.DateField(default=datetime.date.today)),
                ('rent_budget', models.IntegerField(default=0)),
                ('water_supply_budget', models.IntegerField(default=0)),
                ('gas_budget', models.IntegerField(default=0)),
                ('electricity_budget', models.IntegerField(default=0)),
                ('food_expenses_budget', models.IntegerField(default=0)),
                ('communication_expenses_budget', models.IntegerField(default=0)),
                ('transportation_expenses_budget', models.IntegerField(default=0)),
                ('insurance_fee_budget', models.IntegerField(default=0)),
                ('daily_necessities_budget', models.IntegerField(default=0)),
                ('medical_bills_budget', models.IntegerField(default=0)),
                ('entertainment_expenses_budget', models.IntegerField(default=0)),
                ('saving_budget', models.IntegerField(default=0)),
                ('add_item_budget', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Budget',
            },
        ),
    ]
