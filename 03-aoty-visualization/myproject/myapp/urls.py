from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('koleksisaya', views.koleksisaya, name='koleksisaya'),
    path('ratinginput', views.ratinginput, name='ratinginput'),
    path('rekomendasi', views.rekomendasi, name="rekomendasi"),
    path('cfresult', views.cfresult, name="cfresult"),
    path('cbresult', views.cbresult, name="cbresult")
]