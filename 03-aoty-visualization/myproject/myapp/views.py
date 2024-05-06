from django.shortcuts import render


# Create your views here.

import pandas as pd
dfalbum = pd.read_csv('myapp/dataset/albums.csv', sep=';')
dfrating = pd.read_csv('myapp/dataset/albums.csv', sep=';')

album = []
for index, row in dfalbum.iterrows():
    album.append((row['album'], row['artis'], row['thumbnail_album']))

def index(request):
    return render(request, "myapp/index.html", {
        "album_atas": album[0:5],
        "album_bawah": album[5:10]
    })