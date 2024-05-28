from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

df_album = pd.read_csv('myapp/dataset/albums.csv', sep=';')

album = []
for index, row in df_album.iterrows():
    album.append((row['album'], row['artis'], row['thumbnail_album']))



def index(request):
    return render(request, "myapp/index.html", {
        "albums": album[0:300]
    })
    
    
# def rekomendasi(request):
#     return render(request, "myapp/sampah.html", {
#         "albums": album[0:100]
#     })
    
def funsampah(request):
    return render(request, "myapp/sampah.html", {
        "albums": album[0:100]
    })
