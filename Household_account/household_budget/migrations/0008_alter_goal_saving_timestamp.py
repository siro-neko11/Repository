# Generated by Django 4.1 on 2024-01-22 14:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('household_budget', '0007_alter_goal_saving_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal_saving',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
