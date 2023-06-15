from django.urls import path
from . import views

app_name = 'webcaripoule'
urlpatterns = [
    path('top10/', views.top10prep, name="top10prep"),
    path('', views.test_home, name='home'),
    path('difficulte/', views.top10diff, name='diff'),
    path('avis/', views.top10avis, name='avis'),
    path('searchresult/', views.home, name='searchresult'),
    path('cuisson/', views.top10cuiss, name='cuisson'),
]
