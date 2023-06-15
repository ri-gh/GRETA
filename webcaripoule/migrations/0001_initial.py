# Generated by Django 4.2.2 on 2023-06-07 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=100)),
                ('url', models.URLField(max_length=100)),
                ('note', models.FloatField(max_length=100)),
                ('nbre_avis', models.IntegerField()),
                ('difficulte', models.CharField(max_length=10)),
                ('temps_preparation', models.IntegerField()),
                ('temps_cuisson', models.IntegerField()),
                ('ingredients', models.CharField(max_length=100)),
            ],
        ),
    ]
