"""matrix_fiesta URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

import django_cas_ng.views

urlpatterns = [
    path("", include("matrix.urls")),
    path("survey/", include("survey.urls")),
    path("evaluations/", include("evaluations.urls")),
    path("admin/", admin.site.urls),
    path(
        "accounts/login", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"
    ),
    path(
        "accounts/logout",
        django_cas_ng.views.LogoutView.as_view(),
        name="cas_ng_logout",
    ),
]

handler404 = "matrix.views.error_404"
handler500 = "matrix.views.error_500"
handler403 = "matrix.views.error_403"
handler400 = "matrix.views.error_400"

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
