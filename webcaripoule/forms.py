from django import forms


class CariForm(forms.Form):
    recipe = forms.CharField(label="Votre recette", max_length=100)
