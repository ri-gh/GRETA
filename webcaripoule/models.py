from django.db import models
# Create your models here.

class Recipe(models.Model):
    titre = models.CharField(max_length=100)
    url = models.URLField(max_length=100)
    note = models.FloatField(max_length=100)
    nbre_avis = models.IntegerField()
    difficulte = models.CharField(max_length=10)
    temps_preparation = models.IntegerField()
    temps_cuisson = models.IntegerField()
    ingredients = models.CharField(max_length=100)

    def __str__(self):
        return self.titre
