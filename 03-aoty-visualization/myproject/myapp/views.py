# ------------------------------
# Import library yang diperlukan
# ------------------------------
# Library pandas untuk data
import pandas as pd
# Library Django untuk HTTTP Response
from django.http import HttpResponse
# Library Django untuk render HTML
from django.shortcuts import render
# Library FuzzyWuzzy untuk search query
from fuzzywuzzy import fuzz

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
    pass  # Lewatkan


# Function untuk collaborative filtering
# --------------------------------------
def content_based_filtering(df_albums):
    pass  # Lewatkan


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
        # Convert DataFrame album menjadi list dictionary
        album_rated = convert_df_to_list(album_rated)

        # Buka DataFrame hasil Collaborative Filtering dan Content-Based Filtering
        df_cf = pd.read_csv('myapp/dataset/cf_result.csv', sep=',')
        df_cb = pd.read_csv('myapp/dataset/cb_result.csv', sep=',')

        # Convert DataFrame hasil rekomendasi menjadi list dictionary
        rekomendasi_cf = convert_df_to_list(df_cf)
        rekomendasi_cb = convert_df_to_list(df_cb)

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
