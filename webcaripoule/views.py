from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Case, When
from .models import Recipe
from .forms import CariForm
import csv
import os
import pandas as pd
import plotly.express as px
from .urls_spider import run
from .test_cleaning import datacleaning


# Create your views here.

def test_home(request):
    recette = request.POST.get('recette', '').replace(' ', '+')
    recette = recette.replace('é', 'e')

    if recette != '':
        run(recette)

        if os.stat("all_urls.csv").st_size == 0:  # pour tester si le fichier est vide = pas de recette trouvée
            recette = request.POST.get('recette', '')
            context = {'recette': recette,
                       'fichier_vide': True}
            return render(request, 'webcaripoule/home.html', context)

        else:
            datacleaning()
            path = 'fichier_clean.csv'
            Recipe.objects.all().delete()  # pour réinitialiser la base à vide
            with open(path) as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    recipe = Recipe.objects.get_or_create(
                        titre=row[1],
                        url=row[2],
                        note=row[3],
                        nbre_avis=row[4],
                        difficulte=row[5],
                        temps_preparation=row[6],
                        temps_cuisson=row[7],
                        ingredients=row[8], )

            recipe_list = Recipe.objects.all().order_by('-note', '-nbre_avis')
            # le "-" permet de classer par ordre descendant
            # ici on ordonne par 2 critères
            paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            recette = request.POST.get('recette')
            countlen = Recipe.objects.all().count()
            countdiff = Recipe.objects.values('difficulte').annotate(count=Count('pk')).order_by('-count')
            note_moyenne = Recipe.objects.all().aggregate(Avg('note'))
            note_moyenne = round(note_moyenne['note__avg'], 2)
            tps_prep_moyen = Recipe.objects.all().aggregate(Avg('temps_preparation'))
            tps_prep_moyen = tps_prep_moyen['temps_preparation__avg']
            tps_cuisson_moyen = Recipe.objects.all().aggregate(Avg('temps_cuisson'))
            tps_cuisson_moyen = tps_cuisson_moyen['temps_cuisson__avg']
            dico = {}
            for line in countdiff:
                dico[line['difficulte']] = line['count']

            df = pd.read_csv('fichier_clean.csv')
            df_pie = df.groupby('niveau de difficulté').count()
            df_pie = df_pie.reset_index()
            df_pie = df_pie[['niveau de difficulté', 'Unnamed: 0']]
            df_pie = df_pie.rename(columns={'Unnamed: 0': "count"})

            fig_pie = px.pie(df_pie, values='count', names='niveau de difficulté',
                             # color_discrete_sequence=px.colors.qualitative.Set1,
                             color_discrete_map={"très facile": "green",
                                                 "facile": "blue",
                                                 "moyen": "yellow",
                                                 "difficile": "orange",
                                                 "Non_renseigné": "white",
                                                 "très difficile": "red"},
                             title=f'Repartition des niveaux de difficulté pour la recette de "{recette}"')
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', )  # to put the label inside the pie
            fig_pie.update_traces(hole=.4)  # to change the pie chart to donut chart
            fig_pie.update_layout(legend_title_text="Niveaux de difficulté",
                                  template='plotly_dark',
                                  legend=dict(font=dict(color="black")),  # to change color of the legend
                                  title_font_color="black",  # to change the color of the figure title
                                  paper_bgcolor='white',  # to change the background color of the figure
                                  plot_bgcolor='white')  # to change the background colour of the graph
            fig = fig_pie.write_image('webcaripoule/static/webcaripoule/images/pie_image.png')

            context = {'figure': fig,
                       'nbre_recettes': countlen,
                       'page_obj': page_obj,
                       'count': dico,
                       'notemoyenne': note_moyenne,
                       'tpsprepmoy': tps_prep_moyen,
                       'tpscuissmoy': tps_cuisson_moyen,
                       'recette': recette,

                       }
            return render(request, 'webcaripoule/home.html', context)

    else:
        form = CariForm()
        return render(request, 'webcaripoule/home.html', {'form': form})


def home(request):
    recipe_list = Recipe.objects.all().order_by('-note', '-nbre_avis')
    # le "-" permet de classer par ordre descendant
    # ici on ordonne par 2 critères

    paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    countlen = Recipe.objects.all().count()

    context = {
        'nbre_recettes': countlen,
        'page_obj': page_obj,
    }

    return render(request, 'webcaripoule/result.html', context)


def top10prep(request):
    # on va filtrer les 10 recettes avec le temps de préparation les plus courts
    recipe_list = Recipe.objects.all().order_by('temps_preparation')
    paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'recipe_list': recipe_list,
               'page_obj': page_obj, }
    return render(request, 'webcaripoule/details.html', context)


def top10cuiss(request):
    # on va filtrer les 10 recettes avec le temps de cuisson les plus courts
    recipe_list = Recipe.objects.all().order_by('temps_cuisson')
    paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'recipe_list': recipe_list,
               'page_obj': page_obj, }
    return render(request, 'webcaripoule/cuisson.html', context)


def top10diff(request):
    # on va filtrer les 10 recettes avec la difficulté
    # on définit l'ordre de chaque niveau de difficulté en lui attribuant un chiffre
    # pour ensuite ordonner par cet ordre
    recipe_list = Recipe.objects.all().annotate(relevancy=Case(
        When(difficulte='très facile', then=1),
        When(difficulte='facile', then=2),
        When(difficulte='moyen', then=3),
        When(difficulte='difficile', then=4),
        When(difficulte='très difficile', then=5),
        When(difficulte='Non_renseigné', then=6),
    )).order_by('relevancy')
    paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'recipe_list': recipe_list,
               'page_obj': page_obj, }
    return render(request, 'webcaripoule/diff.html', context)


def top10avis(request):
    # on va filtrer les 10 recettes avec la difficulté
    recipe_list = Recipe.objects.all().order_by('-nbre_avis', '-note')
    paginator = Paginator(recipe_list, 10)  # shows 10 recipes per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'recipe_list': recipe_list,
               'page_obj': page_obj, }
    return render(request, 'webcaripoule/avis.html', context)

