import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as plt
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from flask import *
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import numpy as np
except:
    install("numpy")
    import numpy as np
try:
    import pandas as pd
except:
    install("pandas")
    import pandas as pd
try:
    import re
except:
    install("re")
    import re
try:
    import requests as rq
except:
    install("requests")
    import requests as rq
try:
    from bs4 import BeautifulSoup
except:
    install("bs4")
    from bs4 import BeautifulSoup
try:
    import json
except:
    install("json")
    import json



try:

    app = Flask(__name__)


    @app.route('/')
    def index():
        return render_template("index.html")




    @app.route('/home', methods=['POST'])
    def getvalue():

        try:
            a = request.form['name']
            col_name = ['user_id', 'item_id', 'rating', 'timestamp']
            df = pd.read_csv('u.data', sep='\t', names=col_name)
            # print(df.head())
            movietitle = pd.read_csv('Movie_Id_Titles')
            # print(movietitle.head())

            df = pd.merge(df, movietitle, on='item_id')
            # print(df.head())
            # sns.set_style('white')
            # print(df.groupby('title')['rating'].mean().sort_values(ascending=False).head())
            # print('___________________________________________________')
            # print(df.groupby('title')['rating'].count().sort_values(ascending=False).head())
            ratings = pd.DataFrame(df.groupby('title')['rating'].mean())
            ratings['No of ratings'] = pd.DataFrame(df.groupby('title')['rating'].count())
            # print(ratings.head())
            ratings['No of ratings'].hist(bins=80)
            ratings['rating'].hist(bins=80)
            arr = []
            arr1 = []
            # sns.jointplot(x='rating',y='No of ratings',data=ratings,alpha=0.5)
            # plt.show()

            mm = df.pivot_table(index='user_id', columns='title', values='rating')
            # print(mm.head())
            # print(ratings.sort_values('No of ratings',ascending=False).head(10))

            starwar_rate = mm[a]
            # print(starwar_rate.head())

            # now to set correlation

            same_as_starwars = mm.corrwith(starwar_rate)

            corr_starwars = pd.DataFrame(same_as_starwars, columns=['Correlation'])
            corr_starwars.dropna(inplace=True)
            # print(corr_starwars.sort_values('Correlation',ascending=False).head(15))
            corr_starwars = corr_starwars.join(ratings['No of ratings'])
            # print(corr_starwars.head())
            temp = corr_starwars[corr_starwars['No of ratings'] > 100].sort_values('Correlation',
                                                                                   ascending=False).head().index
            for x in temp:
                print(x)
                arr.append(x)
            print(x)
            if len(arr) == 0:
                arr1 = "Please Enter A Movie Name"
            else:
                arr1 = arr
        except:
            arr1 = "Movie not available"

        return render_template("show.html", name=arr1)


    @app.route('/books', methods=['POST'])
    def getbooks():
        df_book = pd.read_csv("book.csv", error_bad_lines=False)
        df_book['average_rating'] = df_book['average_rating'].astype(float)
        ############## Take user input ###################
        book_name = request.form['bookss']
        r = rq.get('https://www.google.com/search?q=books+similar+to+%s' % book_name)
        soup = BeautifulSoup(r.text, 'html.parser')
        p = soup.find(id='main')
        sr = p.find_all('a')
        result = re.findall(r'//www.goodreads.com/book/similar/(\w+)', str(sr))
        r2 = rq.get('https://www.goodreads.com/book/similar/%s' % result[0])
        soup2 = BeautifulSoup(r2.text, 'html.parser')
        booksClass = soup2.find_all('div', attrs={'class': 'listWithDividers__item'})
        FinalBookArray = []  # will contain final suggested books

        if len(booksClass) >= 6:
            for booksCount in range(1, 6):
                FinalBookArray.append(booksClass[booksCount].find('span', attrs={'itemprop': 'name'}).contents[0])

        else:
            for books in booksClass:
                FinalBookArray.append(books.find('span', attrs={'itemprop': 'name'}).contents[0])
        print(FinalBookArray)  # array with final book values
        return render_template("show.html", book=FinalBookArray)


    @app.route('/songs', methods=['POST'])
    def getsongs():
        songmetadata = pd.read_csv(r'song_data.csv')
        othersongdata = pd.read_fwf(r'1000.txt')
        othersongdata.columns = ['user_id', 'song_id', 'listen_count']
        song_df = pd.merge(othersongdata, songmetadata.drop_duplicates(['song_id']), on="song_id", how="left")
        song_grouped = pd.DataFrame(song_df.groupby('song_id')['listen_count'].count())
        song_grouped = pd.DataFrame(song_df.groupby('song_id')['listen_count'].count())
        song_df.astype({'listen_count': 'int32'}, {'song_id': 'str'}).dtypes
        id = None
        print("Enter Song Name (Try --Fix You--):")
        name = request.form['songs']
        for i in range(len(song_df['title'])):
            if (name == song_df['title'][i]):
                id = song_df['song_id'][i]
                break
        song_df[song_df['song_id'] == id]
        songs_crosstab = pd.pivot_table(song_df, values='listen_count', index='user_id', columns='song_id')
        songs_crosstab.head()
        predictor_song_ratings = songs_crosstab[id]
        predictor_song_ratings[predictor_song_ratings >= 1]
        similar_songs = songs_crosstab.corrwith(predictor_song_ratings)
        corr_listened_song = pd.DataFrame(similar_songs, columns=['value'])
        corr_listened_song.dropna(inplace=True)
        predictor_corr_summary = corr_listened_song.join(song_grouped['listen_count'])
        predictor_corr_summary = predictor_corr_summary.sort_values('value', ascending=False)
        final_recommended_songs = predictor_corr_summary[predictor_corr_summary.value < 0.9999]
        final_recommended_songs.sort_values('value', ascending=False)
        final_recommended_songs = final_recommended_songs.reset_index()
        song_df_one = song_df.drop(['listen_count'], axis=1)
        similar_songs = pd.merge(final_recommended_songs, song_df_one.drop_duplicates(["song_id"]), on="song_id",
                                 how="left")
        similar_songs = similar_songs.sort_values('value', ascending=False)
        similar_songs.head(5)
        print(similar_songs)
        return render_template("show.html", song=similar_songs)


except:
    print("Movie Not Available")

            
if __name__ == '__main__':
    app.run(debug=True)
