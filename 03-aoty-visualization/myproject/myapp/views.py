from django.shortcuts import render


# Create your views here.

import pandas as pd
dfalbum = pd.read_csv('myapp/dataset/albums.csv', sep=';')
dfrating = pd.read_csv('myapp/dataset/albums.csv', sep=';')
artists = dfalbum['artis']

def index(request):
    return render(request, "myapp/index.html", {
        "artists": artists
    })