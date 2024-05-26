from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('sampah', views.funsampah, name="sampah")
]