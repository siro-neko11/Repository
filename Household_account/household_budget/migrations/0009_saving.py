# Generated by Django 4.1 on 2024-01-22 14:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('household_budget', '0008_alter_goal_saving_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Saving',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('year_month', models.CharField(max_length=7)),
                ('saving', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='savings_for_balance', to='household_budget.balanceofpayments')),
                ('user', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'savings',
            },
        ),
    ]
