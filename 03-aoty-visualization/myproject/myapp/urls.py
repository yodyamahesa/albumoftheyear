from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('sampah', views.funsampah, name="sampah"),
    path('koleksisaya', views.koleksisaya, name='koleksisaya'),
    path('ratinginput', views.ratinginput, name='ratinginput'),
    path('hasil', views.rekomendasi, name="hasil")
]