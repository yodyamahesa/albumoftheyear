# ------------------------------
# Import library yang diperlukan
# ------------------------------
# Library numpy untuk array
import numpy as np
# Library pandas untuk data
import pandas as pd
# Library Django untuk HTTTP Response
from django.http import HttpResponse
# Library Django untuk render HTML
from django.shortcuts import render
# Library FuzzyWuzzy untuk search query
from fuzzywuzzy import fuzz
# Library TF-IDF
from sklearn.feature_extraction.text import TfidfVectorizer
# Library Cosine Similarity
from sklearn.metrics.pairwise import cosine_similarity

# Library scikit-learn untuk rekomendasi similarity

# --------------------------------------------
# DataFrame dataset albums.csv dan ratings.csv
# --------------------------------------------
# Baca csv ratings.csv dengan separator titik koma
df_rating = pd.read_csv('myapp/dataset/ratings.csv', sep=';')
# Baca csv albums.csv dengan separator titik koma
df_album = pd.read_csv('myapp/dataset/albums.csv', sep=';')
# Cleaning untuk separator data titik koma garis menjadi koma
df_album = df_album.apply(lambda x: x.str.replace(';|', ', '))
# Isi input rating menjadi -1 untuk rating album awal
df_album['input'] = -1


# ----------------------------
# Function Utama Untuk Program
# ----------------------------
# Function untuk mengubah DataFrame ke list dictionary
# ----------------------------------------------------
def convert_df_to_list(df):
    # Variabel list kosong untuk menyimpan hasil convert
    results = list()
    # Looping setiap row pada DataFrame
    for row in df.to_dict(orient='records'):
        # Menambahkan dictionary masing-masing row ke list
        results.append(row)
    # Kembalikan hasil convert
    return results


# Function untuk search query album
# ---------------------------------
def search_album(df, query):
    # Buat kolom artis album untuk menyimpan gabungan artis dan album
    df['artis_album'] = df['artis'] + ' - ' + df['album']
    # Buat kolom fuzzy score untuk menyimpan hasil skor fuzzy search
    df['fuzzy_score'] = df['artis_album'].apply(lambda x: fuzz.token_sort_ratio(x, query))
    # Ambil top 20 album tercocok teratas
    top_results = df.sort_values(by='fuzzy_score', ascending=False).head(20)
    # Kembalikan hasil search
    return top_results


# Function untuk collaborative filtering
# --------------------------------------
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
    sorted = sorted[sorted['input'] == -1]
    top_10 = sorted.head(10)

    return top_10


# Function untuk collaborative filtering
# --------------------------------------
def content_based_filtering(df_albums, links):
    tabel = pd.DataFrame({
        'link_album': df_albums['link_album'],
        'genre': df_albums['genre'],
        'artis': df_albums['artis'],
        'label': df_albums['label'],
        'produser': df_albums['produser'],
        'penulis': df_albums['penulis']
    })

    tabel = tabel.apply(lambda x: x.str.replace(' ', '_'))
    tabel = tabel.apply(lambda x: x.str.replace('!', ''))
    tabel = tabel.apply(lambda x: x.str.replace('-', '_'))
    tabel = tabel.apply(lambda x: x.str.replace("'", '_'))
    tabel = tabel.apply(lambda x: x.str.replace(',', ' '))

    combined = pd.DataFrame({
        'link_album': tabel['link_album'],
        'corpus': tabel[['genre', 'artis', 'label', 'produser', 'penulis']].apply(lambda x: ' '.join(map(str, x)),
                                                                                  axis=1)
    })

    combined = combined.set_index('link_album')
    combined = combined.apply(lambda x: x.str.replace('nan', ''))
    corpus = combined.corpus.tolist()

    def tfidf_similarity(query):
        tfidf_vectorizer = TfidfVectorizer()
        corpus = combined['corpus'].values
        tfidf_vectorizer.fit(corpus)
        query_tfidf = tfidf_vectorizer.transform([query])
        corpus_tfidf = tfidf_vectorizer.transform(corpus)
        similarity_scores = query_tfidf.dot(corpus_tfidf.T)
        similarity_scores_dense = similarity_scores.toarray()
        sorted_indices = np.argsort(similarity_scores_dense)[0][::-1]
        relevant_links = combined.index[sorted_indices].tolist()
        tfidf_scores = similarity_scores_dense[0][sorted_indices]
        result = pd.DataFrame({'link_album': relevant_links, 'tfidf_score': tfidf_scores}).set_index('link_album')
        return result

    def get_score(links):
        for i in range(len(links)):
            links[i] = links[i].replace("-", "_")
        query = combined.loc[combined.index.isin(links)]
        column_values = query['corpus'].astype(str)
        combined_string = ' '.join(column_values)
        words = combined_string.split()
        unique_words = list(set(words))
        query = ' '.join(unique_words)
        result = tfidf_similarity(query)
        result.index = result.index.str.replace('_', '-')
        df_result = df_albums.join(result, on='link_album')
        sorted = df_result.sort_values(by='tfidf_score', ascending=False)
        sorted = sorted[sorted['input'] == -1]
        top_10 = sorted.head(10)
        return top_10

    top_10 = get_score(links)
    return top_10


# ----------------------------------------
# Kode Function Utama Handler Request HTML
# ----------------------------------------
# Function untuk menghandle request ke halaman HomePage
# -----------------------------------------------------
def index(request):
    # Jika request dalam method GET
    # -----------------------------
    if request.method == 'GET':
        # Convert DataFrame album menjadi list dictionary
        albums_list = convert_df_to_list(df_album)
        # Render HTML
        return render(request, "myapp/index.html", {
            "albums": albums_list[:100]
        })

    # Jika request dalam method POST
    # ------------------------------
    elif request.method == 'POST':
        # Ambil key-key POST
        query = request.POST.get('Search Query')
        link_album = request.POST.get('link_album')
        # Jika POST terdapat key 'Search Query'
        # -------------------------------------
        if query:
            # Melakukan search album
            search_results = search_album(df_album.copy(), query)
            # Convert DataFrame album menjadi list dictionary
            search_results = convert_df_to_list(search_results)
            # Render HTML
            return render(request, "myapp/index.html", context={
                "albums": search_results
            })
        # Jika POST terdapat key 'link_album'
        # -----------------------------------
        elif link_album:
            # Hapus rating album tersebut dan jadikan default -1
            df_album.loc[df_album['link_album'] == f'{link_album}', 'input'] = -1
            # Convert DataFrame album menjadi list dictionary
            albums_list = convert_df_to_list(df_album)
            # Render HTML
            return render(request, "myapp/index.html", {
                "albums": albums_list[:100]
            })
        # Jika POST tidak terdapat key apapun
        # -----------------------------------
        else:
            # Convert DataFrame album menjadi list dictionary
            albums_list = convert_df_to_list(df_album)
            # Render HTML
            return render(request, "myapp/index.html", {
                "albums": albums_list[:100]
            })

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan


# Function untuk menghandle request ke halaman Koleksi Saya
# ---------------------------------------------------------
def koleksisaya(request):
    # Jika request dalam method GET
    # -----------------------------
    if request.method == 'GET':
        # Ambil album yang telah dirating / tidak bernilai -1
        album_rated = df_album[df_album['input'] != -1]
        # Convert DataFrame album menjadi list dictionary
        album_rated = convert_df_to_list(album_rated)
        # Render HTML
        return render(request, 'myapp/koleksisaya.html', {
            "albums": album_rated
        })

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan


# Function untuk menghandle request ke halaman Input Rating
# ---------------------------------------------------------
def ratinginput(request):
    # Jika request dalam method POST
    # -----------------------------
    if request.method == 'POST':
        # Ambil key-key POST
        link_album = request.POST.get('link_album')
        rating = request.POST.get('nilairating')
        # Jika POST terdapat key 'nilairating'
        # -------------------------------------
        if rating:
            # Update rating album di df_album sesuai dengan input rating
            df_album.loc[df_album['link_album'] == f'{link_album}', 'input'] = int(rating)

        # Mengambil row album sesuai dengan link_album
        clicked_df = df_album[df_album['link_album'] == link_album]

        # Ambil nilai rating dari album tersebut
        ratingnya = int(clicked_df['input'].iloc[0])

        # Convert DataFrame album menjadi list dictionary
        albums_list = convert_df_to_list(clicked_df)

        # Pass nilai rating 0 jika nilainya -1
        if ratingnya == -1:
            ratingnya = 0
        # Lewatkan nilai rating jika rating lainnya
        else:
            pass  # Lewatkan

        # Render HTML
        return render(request, 'myapp/ratinginput.html', {
            "albumdetails": albums_list,
            "ratingnya": ratingnya
        })

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan


# Function untuk menghandle request ke halaman rekomendasi
# --------------------------------------------------------
def rekomendasi(request):
    # Jika request dalam method GET
    # -----------------------------
    if request.method == 'GET':
        # Ambil album yang telah dirating / tidak bernilai -1
        album_rated = df_album[df_album['input'] != -1]

        # Collaborative Filtering
        user_cf = list(zip(album_rated['link_album'].values, album_rated['input'].values))
        hasil_cf = collaborative_filtering(df_rating, df_album, user_cf)

        # Content-Based Filtering
        user_cb = album_rated['link_album'].to_list()
        hasil_cb = content_based_filtering(df_album, user_cb)

        # Simpan Hasil Collaborative Filtering dan Content-Based Filtering
        save_cf = pd.DataFrame({
            'link_album': hasil_cf['link_album'],
            'album': hasil_cf['album'],
            'artis': hasil_cf['artis'],
            'score': hasil_cf['score']
        })
        save_cb = pd.DataFrame({
            'link_album': hasil_cb['link_album'],
            'album': hasil_cb['album'],
            'artis': hasil_cb['artis'],
            'score': hasil_cb['tfidf_score']
        })

        # Round Score
        save_cf['score'] = save_cf['score'].round(4)
        save_cb['score'] = save_cb['score'].round(4)

        # Round Score
        hasil_cf['score'] = hasil_cf['score'].round(4)
        hasil_cb['tfidf_score'] = hasil_cb['tfidf_score'].round(4)

        # Looping memberi index
        hasil_cf['rank'] = range(1, len(hasil_cf) + 1)
        hasil_cb['rank'] = range(1, len(hasil_cb) + 1)

        save_cf['index'] = range(1, len(save_cf) + 1)
        save_cf = save_cf.set_index('index')
        save_cf.to_csv('myapp/dataset/cf_result.csv', sep=',', index=True)

        save_cb['index'] = range(1, len(save_cb) + 1)
        save_cb = save_cb.set_index('index')
        save_cb.to_csv('myapp/dataset/cb_result.csv', sep=',', index=True)

        # Convert DataFrame album menjadi list dictionary
        album_rated = convert_df_to_list(album_rated)
        hasil_cf = convert_df_to_list(hasil_cf)
        hasil_cb = convert_df_to_list(hasil_cb)

        # Convert DataFrame hasil rekomendasi menjadi list dictionary
        rekomendasi_cf = hasil_cf
        rekomendasi_cb = hasil_cb

        # Render HTML
        return render(request, 'myapp/rekomendasi.html', {
            "albums": album_rated,
            "rekomendasi_cf": rekomendasi_cf,
            "rekomendasi_cb": rekomendasi_cb
        })

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan


# Function untuk menghandle request ke file csv Collaborative Filtering
# ---------------------------------------------------------------------
def cfresult(request):
    # Jika request dalam method GET
    # -----------------------------
    if request.method == 'GET':
        # Lokasi file csv
        file_path = 'myapp/dataset/cf_result.csv'
        # Buka file csv
        with open(file_path, 'rb') as f:
            # Membuat objek response yang berisi file csv
            response = HttpResponse(f.read(), content_type='text/csv')
            # Deklarasi header bahwa ini merupakan attachment file csv
            response['Content-Disposition'] = 'attachment; filename="cf_result.csv"'
            # Mengembalikan file csv ke request
            return response

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan


# Function untuk menghandle request ke file csv Content-Based Filtering
# ---------------------------------------------------------------------
def cbresult(request):
    # Jika request dalam method GET
    # -----------------------------
    if request.method == 'GET':
        # Lokasi file csv
        file_path = 'myapp/dataset/cb_result.csv'
        # Buka file csv
        with open(file_path, 'rb') as f:
            # Membuat objek response yang berisi file csv
            response = HttpResponse(f.read(), content_type='text/csv')
            # Deklarasi header bahwa ini merupakan attachment file csv
            response['Content-Disposition'] = 'attachment; filename="cb_result.csv"'
            # Mengembalikan file csv ke request
            return response

    # Jika request dalam method lain
    # ------------------------------
    else:
        pass  # Lewatkan

# KODE FILTERING DIPAKE LAGI NANTI
# --------------------------------
# filtered_rows = df_album[df_album['input'] != -1]
# user_ratings_cf = list(zip(filtered_rows['link_album'].values, filtered_rows['input'].values))
# filtered_rows = df_album[df_album['input'] >= 50]
# user_ratings_cb = filtered_rows['link_album'].to_list()
# print('collaborative filtering')
# print(user_ratings_cf)
# print('content based filtering')
# print(user_ratings_cb)
