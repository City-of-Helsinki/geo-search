# Generated by Django 3.2.7 on 2021-09-16 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("address", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="municipality",
            options={"verbose_name_plural": "municipalities"},
        ),
        migrations.AlterField(
            model_name="municipalitytranslation",
            name="name",
            field=models.CharField(
                db_index=True, default="", max_length=100, verbose_name="Name"
            ),
            preserve_default=False,
        ),
    ]