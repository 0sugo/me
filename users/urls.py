"""SOMA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
import datetime

from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('signup', views.signup, name="signup"),
    path("profile", views.profile, name="profile"),
    path("logout", views.logout, name="logout"),
    path("login", views.login, name="login"),
    path("reset_link_gen", views.reset_link_gen, name="reset"),
    path("password_reset/<email>", views.password_reset, name="password-reset"),
    path("activate/<unique>", views.activate, name="activate"),

]
