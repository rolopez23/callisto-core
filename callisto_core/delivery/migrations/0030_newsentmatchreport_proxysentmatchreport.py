# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-22 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("delivery", "0029_auto_20171122_1448")]

    operations = [
        migrations.CreateModel(
            name="NewSentMatchReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sent", models.DateTimeField(auto_now_add=True)),
                ("to_address", models.TextField(null=True)),
                ("reports", models.ManyToManyField(to="delivery.MatchReport")),
            ],
        ),
        migrations.CreateModel(
            name="ProxySentMatchReport",
            fields=[],
            options={"proxy": True, "indexes": []},
            bases=("delivery.newsentmatchreport",),
        ),
    ]
