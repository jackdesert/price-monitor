# Generated by Django 2.1.4 on 2018-12-31 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simpletire', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='in_stock',
            field=models.BooleanField(),
        ),
    ]
