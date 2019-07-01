from django.urls import path, re_path

from matrix import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('ues/liste/', views.liste_ues, name="ues.liste"),

    re_path(r'ues/matrix/(?P<slug>[-\w]+)', views.matrix_ecue, name="ues.matrix_ecue"),

    path('connexion/', 
            views.connexion, 
            name='users.connexion'),
    path('deconnexion/',
            views.deconnexion,
            name='users.deconnexion'),
]


