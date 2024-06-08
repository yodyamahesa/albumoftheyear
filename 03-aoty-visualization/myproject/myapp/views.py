from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from fuzzywuzzy import fuzz

# Dataframe dataset album
df_album = pd.read_csv('myapp/dataset/albums.csv', sep=';')

# Menyimpan data rating album user
user_ratings = list()

def search_album(df, query):

    df['artis album'] = df['artis'] + ' - ' + df['album']
    df['Score'] = df['artis album'].apply(lambda x: fuzz.token_sort_ratio(x, query))
    top_results = df.sort_values(by='Score', ascending=False).head(20)  # Ambil 3 hasil teratas

    # Kembalikan daftar tuple (album, artis, thumbnail)
    results = []
    for _, row in top_results.iterrows():
        results.append((row['album'], row['artis'], row['thumbnail_album'], row['link_album']))

    return results

album = []
for index, row in df_album.iterrows():
    album.append((row['album'], row['artis'], row['thumbnail_album'], row['link_album']))

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
    
def koleksisaya(request):
    return render(request, 'myapp/koleksisaya.html')

def ratinginput(request):
    if request.method == 'POST':
        link_album = request.POST.get('link_album')

        # Do something with the thumbnail (e.g., save it to the database or process it)
        print(f"Received link album: {link_album}")  # Example: Just print it for now

        clicked_df = df_album[df_album['link_album'] == link_album]
        results = []
        for _, row in clicked_df.iterrows():
            results.append((row['album'], row['artis'], row['thumbnail_album'], row['label'], row['genre'], row['tanggal_rilis'], row['produser'], row['penulis'], row['thumbnail_artis']))

        return render(request, 'myapp/ratinginput.html', {
            "albumdetails": results
        })

def detail_album(request, album_id):
    # Baca data dari file CSV
    with open('albums.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';|')  # Gunakan ';|' sebagai pemisah
        albumdetails = []
        for row in reader:
            # Ubah pemisah di kolom Label, Genre, Produser, Penulis
            row[7] = row[7].replace(';|', ',')  # Kolom Label
            row[8] = row[8].replace(';|', ',')  # Kolom Genre
            row[9] = row[9].replace(';|', ',')  # Kolom Produser
            row[10] = row[10].replace(';|', ',')  # Kolom Penulis
            albumdetails.append(row)

    # Temukan album yang sesuai dengan album_id
    album = None
    for row in albumdetails:
        if row[2] == album_id:  # Asumsi kolom album_id adalah kolom ke-3 (index 2)
            album = row
            break

    if album:
        context = {
            'albumdetails': [album],  # Kirim hanya data album yang sesuai
            # ... (variabel lain yang dibutuhkan template Anda)
        }
        return render(request, 'ratinginput.html', context)
    else:
        # Tampilkan pesan error jika album tidak ditemukan
        return render(request, 'error.html', {'message': 'Album tidak ditemukan'})

def rekomendasi(request):
    return render(request, "myapp/sampah.html", {
        "albums": album[0:100]
    })
    
def funsampah(request):
    return render(request, "myapp/sampah.html", {
        "albums": album[0:100]
    })


#search_album(df_album, "taylor")