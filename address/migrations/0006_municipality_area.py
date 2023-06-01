# Generated by Django 4.2.1 on 2023-05-24 11:26

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("address", "0005_address_municipality"),
    ]

    operations = [
        migrations.AddField(
            model_name="municipality",
            name="area",
            field=django.contrib.gis.db.models.fields.MultiPolygonField(
                blank=True, null=True, srid=4326
            ),
        ),
    ]