# Generated by Django 4.1 on 2024-01-22 12:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('household_budget', '0005_alter_goal_saving_month_delete_saving'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal_saving',
            name='month',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='goal_saving',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
