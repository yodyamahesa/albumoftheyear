from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from fuzzywuzzy import fuzz

df_album = pd.read_csv('myapp/dataset/albums.csv', sep=';')

def search_album(df, query):

    df['artis album'] = df['artis'] + ' - ' + df['album']
    df['Score'] = df['artis album'].apply(lambda x: fuzz.token_sort_ratio(x, query))
    top_results = df.sort_values(by='Score', ascending=False).head(10)  # Ambil 3 hasil teratas

    # Kembalikan daftar tuple (album, artis, thumbnail)
    results = []
    for _, row in top_results.iterrows():
        results.append((row['album'], row['artis'], row['thumbnail_album']))

    return results

album = []
for index, row in df_album.iterrows():
    album.append((row['album'], row['artis'], row['thumbnail_album']))

def index(request):
    if request.method == 'POST':
        query = request.POST.get('Search Query')
        if query != "" :
            # Lakukan pencarian album berdasarkan query
            search_results = search_album(df_album.copy(), query)
            return render(request, "myapp/index.html", {
                "albums": search_results  #  Pass the list of tuples directly
            })

    # Jika bukan POST atau query kosong, tampilkan hasil default
    return render(request, "myapp/index.html", {
        "albums": album[0:100]  # Ambil 100 album pertama
    })
    

def rekomendasi(request):
    return render(request, "myapp/sampah.html", {
        "albums": album[0:100]
    })
    
def funsampah(request):
    return render(request, "myapp/sampah.html", {
        "albums": album[0:100]
    })




#search_album(df_album, "taylor")