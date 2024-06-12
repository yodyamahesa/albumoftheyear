from django.shortcuts import render
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from fuzzywuzzy import fuzz
from sklearn.metrics.pairwise import cosine_similarity

# Dataframe dataset album
df_rating = pd.read_csv('myapp/dataset/ratings.csv', sep=';')
df_album = pd.read_csv('myapp/dataset/albums.csv', sep=';')
df_album = df_album.apply(lambda x: x.str.replace(';|', ', '))
df_album['input'] = -1

# Menyimpan data rating album user
user_ratings = list()

def search_album(df, query):
    df['artis album'] = df['artis'] + ' - ' + df['album']
    df['Score'] = df['artis album'].apply(lambda x: fuzz.token_sort_ratio(x, query))
    top_results = df.sort_values(by='Score', ascending=False).head(20)  # Get top 20 results

    # Return a list of tuples (album, artis, thumbnail, link_album, input)
    results = []
    for _, row in top_results.iterrows():
        results.append((row['album'], row['artis'], row['thumbnail_album'], row['link_album'], row['input']))

    return results

def collaborative_filtering(df_ratings, df_albums, user_ratings):
    # Create interaction matrix
    interaction_matrix = df_ratings.pivot_table(index='user', columns='link_album', values='rating_album')
    df_filled = interaction_matrix.fillna(0)

    # Standardize ratings
    def standardize(row):
        return (row - row.mean()) / (row.max() - row.min())

    ratings_std = df_filled.apply(standardize).fillna(0)

    # Calculate item similarity
    item_similarity = cosine_similarity(ratings_std.T)
    item_similarity_df = pd.DataFrame(item_similarity, index=ratings_std.columns, columns=ratings_std.columns)

    # Function to get similar albums
    def get_similar_more_albums(user_ratings):
        total_scores = pd.Series(dtype=float)
        for album, rating in user_ratings:
            similar_scores = item_similarity_df[album] * (rating - 50)
            total_scores = total_scores.add(similar_scores, fill_value=0)
        total_scores = total_scores.sort_values(ascending=False)
        return total_scores

    # Get recommendations
    hasil_data = get_similar_more_albums(user_ratings)
    hasil = pd.DataFrame(hasil_data, columns=['score'])
    hasil['link_album'] = hasil_data.index
    hasil = hasil.reset_index(drop=True)

    # Merge with album details
    df_hasil = df_albums.join(hasil.set_index("link_album"), on='link_album')
    sorted = df_hasil.sort_values(by='score', ascending=False)
    top_10 =sorted.head(10)

    return top_10


def index(request):
    if request.method == 'POST':
        query = request.POST.get('Search Query')
        if query:
            # Perform album search based on query
            search_results = search_album(df_album.copy(), query)
            return render(request, "myapp/index.html", {
                "albums": search_results  # Pass the list of tuples directly
            })
    else:
        # Prepare initial album list
        album_list = []
        for index, row in df_album.iterrows():
            album_list.append((row['album'], row['artis'], row['thumbnail_album'], row['link_album'], row['input']))
        # If not POST or query is empty, display default results
        return render(request, "myapp/index.html", {
            "albums": album_list[:100]  # Get the first 100 albums
        })


def koleksisaya(request):
    return render(request, 'myapp/koleksisaya.html')


def ratinginput(request):
    if request.method == 'POST':
        link_album = request.POST.get('link_album')
        rating = request.POST.get('nilairating')
        # Do something with the thumbnail (e.g., save it to the database or process it)
        print(f"Received link album: {rating}")  # Example: Just print it for now
        print(f"Received link album: {link_album}")  # Example: Just print it for now

        if rating is not None:
            df_album.loc[df_album['link_album'] == f'{link_album}', 'input'] = int(rating)
            filtered_rows = df_album[df_album['input'] != -1]
            user_ratings_cf = list(zip(filtered_rows['link_album'].values, filtered_rows['input'].values))
            filtered_rows = df_album[df_album['input'] >= 50]
            user_ratings_cb = filtered_rows['link_album'].to_list()
            print('collaborative filtering')
            print(user_ratings_cf)
            print('content based filtering')
            print(user_ratings_cb)

        clicked_df = df_album[df_album['link_album'] == link_album]
        results = []
        for _, row in clicked_df.iterrows():
            results.append((row['album'], row['artis'], row['thumbnail_album'], row['label'], row['genre'],
                            row['tanggal_rilis'], row['produser'], row['penulis'], row['thumbnail_artis'],
                            row['link_album']))

        return render(request, 'myapp/ratinginput.html', {
            "albumdetails": results
        })


def detail_album(request, album_id):
    albumdetails = []
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


def getLinkAndRating(request):
    if request.method == 'POST':
        link_album = request.POST.get('link_album')
        rating = request.POST.get('rating')

        # Update the DataFrame with the new rating
        df_album.loc[df_album['link_album'] == link_album, 'input'] = int(rating)
        filtered_rows = df_album[df_album['input'] != -1]

        results = []
        for _, row in filtered_rows.iterrows():
            results.append((row['album'], row['artis'], row['thumbnail_album'], row['label'], row['genre'],
                            row['tanggal_rilis'], row['produser'], row['penulis'], row['thumbnail_artis']))

        return render(request, 'myapp/ratinginput.html', {
            "albumdetails": results
        })
