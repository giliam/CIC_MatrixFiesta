from django.urls import path, re_path

from matrix import views

urlpatterns = [
    path('', views.homepage, name="matrix.homepage"),
    path('eleves/liste/', views.liste_ues, name="ues.liste"),
    path('eleves/', views.matrix_ues, name="ues.matrix"),
    path('enseignants/', views.homepage_teachers, name="ues.homepage_teachers"),

    re_path(r'ues/matrix/(?P<slug>[-\w]+)', views.matrix_ecue, name="ues.matrix_ecue"),
    re_path(r'acquis/evaluer/(?P<slug>[-\w]+)', views.evaluer_acquis, name="ues.evaluer_acquis"),

    path('connexion/', 
            views.connexion, 
            name='users.connexion'),
    path('deconnexion/',
            views.deconnexion,
            name='users.deconnexion'),
]


