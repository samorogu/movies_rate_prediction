import pandas as pd
import re
import numpy as np


class Movies(object):
    """A movie class"""

    def __init__(self, df_movies: pd.DataFrame, df_ratings: pd.DataFrame):
        self.df_movies = self.clean_year_text(df_movies)
        self.df_movies = self.dummy_genres(self.df_movies)
        self.df_movies_history_ratings = self.movie_ratings_agregation(
            df_ratings)

    def clean_year_text(self, movies):
        """Extract the year and exlcude it from the tittle"""

        movies["year"] = movies["title"].str.extract(
            '(\(\d\d\d\d\))', expand=False)
        movies['year'] = movies["year"].str.extract(
            '(\d\d\d\d)', expand=False)  # only numbers
        movies['title'] = movies.title.str.replace(
            '(\(\d\d\d\d\))', '')  # replace numbers and parenthesis
        movies['title'] = movies['title'].apply(lambda x: x.strip())
        return movies

    def dummy_genres(self, movies):
        """dummy clases of the genres"""

        movies['genre_list'] = movies['genres'].str.split('|').tolist()
        flat_genre = [item for sublist in movies['genre_list']
                      for item in sublist]  # flatten the list
        set_genre = set(flat_genre)  # convert to a set to make unique
        unique_genre = list(set_genre)  # back to list
        # remove NA
        unique_genre.remove("(no genres listed)")

        # create columns by each unique genre
        movies = movies.reindex(
            movies.columns.tolist() + unique_genre, axis=1, fill_value=0)

        # for each value inside column, update the dummy
        for index, row in movies.iterrows():
            for val in row["genres"].split('|'):
                if val != "(no genres listed)":
                    movies.loc[index, val] = 1
        return movies

    def movie_ratings_agregation(self, ratings):
        """given a rating dataframe, agregate the ratings of movies in diferent periods of time
        """

        movies_ratings = ratings.groupby(["movieId", "year_month"]).agg({"userId": "count", "rating": ["mean", "median"]})\
            .reset_index()

        movies_ratings.columns = [
            "movieId", "year_month", "count", "mean_rating", "median_rating"]

        movies_ratings["last_1_months_movie_rating"] = movies_ratings.groupby("movieId")['mean_rating'].shift(1)\
            .reset_index()["mean_rating"]

        movies_ratings["last_1_months_movie_rating_counts"] = movies_ratings.groupby("movieId")['count'].shift(1)\
            .reset_index()["count"]
        movies_ratings["mean_3_months_movie_rating"] = movies_ratings.groupby("movieId")['last_1_months_movie_rating'].rolling(3).mean()\
            .reset_index()["last_1_months_movie_rating"]
        movies_ratings["mean_6_months_movie_rating"] = movies_ratings.groupby("movieId")['last_1_months_movie_rating'].rolling(6).mean()\
            .reset_index()["last_1_months_movie_rating"]
        movies_ratings["last_1_month_per_3_months_movie_rating"] = movies_ratings.last_1_months_movie_rating / \
            movies_ratings.mean_3_months_movie_rating
        movies_ratings["last_1_month_per_6_months_movie_rating"] = movies_ratings.last_1_months_movie_rating / \
            movies_ratings.mean_6_months_movie_rating

        # movies_ratings = movies_ratings.loc[:, ~movies_ratings.columns.isin(
        #    ["count", "mean_rating", "median_rating"])]

        return movies_ratings
