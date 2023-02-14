# Generated by Django 4.1.5 on 2023-02-07 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newspaper", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NewsLetter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email", models.EmailField(max_length=254)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
