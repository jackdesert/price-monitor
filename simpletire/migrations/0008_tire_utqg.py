# Generated by Django 2.1.7 on 2019-03-14 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simpletire', '0007_auto_20190311_0904'),
    ]

    operations = [
        migrations.AddField(
            model_name='tire',
            name='utqg',
            field=models.SmallIntegerField(null=True),
        ),
    ]