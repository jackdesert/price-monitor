# Generated by Django 2.1.2 on 2019-01-29 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simpletire', '0003_auto_20181231_1919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reading',
            name='price_pennies',
            field=models.PositiveIntegerField(),
        ),
    ]