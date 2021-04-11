import pandas as pd
import re
import numpy as np

from movies import Movies


class Genres(object):
    """A tag class"""

    def __init__(self, df_movies: pd.DataFrame, df_movie_ratings: pd.DataFrame):
        self.genres_df = self.create_genre_history_rating(
            df_movies, df_movie_ratings)

    def create_genre_history_rating(self, movies, movies_ratings):
        movies_genre_gather = movies[["movieId",
                                      "genre_list"]].explode("genre_list")
        movies_ratings_genre = movies_ratings.merge(
            movies_genre_gather, how="left")

        genre_ratings = movies_ratings_genre.groupby(["genre_list", "year_month"]).agg({"movieId": "count",
                                                                                       "mean_rating": ["mean", "median"]}).reset_index()

        genre_ratings.columns = [
            "genre_list", "year_month", "count", "mean_rating", "median_rating"]

        genre_ratings["last_1_months_genre_rating"] = genre_ratings.groupby(
            "genre_list")['mean_rating'].shift(1).reset_index()["mean_rating"]
        genre_ratings["last_1_months_genre_rating_counts"] = genre_ratings.groupby(
            "genre_list")['count'].shift(1).reset_index()["count"]
        genre_ratings["mean_3_months_genre_rating"] = genre_ratings.groupby("genre_list")[
            'last_1_months_genre_rating'].rolling(3).mean().reset_index()["last_1_months_genre_rating"]
        genre_ratings["mean_6_months_genre_rating"] = genre_ratings.groupby("genre_list")[
            'last_1_months_genre_rating'].rolling(6).mean().reset_index()["last_1_months_genre_rating"]
        genre_ratings["last_1_month_per_3_months_genre_rating"] = genre_ratings.last_1_months_genre_rating / \
            genre_ratings.mean_3_months_genre_rating
        genre_ratings["last_1_month_per_6_months_genre_rating"] = genre_ratings.last_1_months_genre_rating / \
            genre_ratings.mean_6_months_genre_rating

        # now we will paste the genre variables
        genre_variables = ["genre_list", "year_month", "last_1_months_genre_rating", "mean_3_months_genre_rating",
                           "mean_6_months_genre_rating", "last_1_month_per_3_months_genre_rating",
                           "last_1_month_per_6_months_genre_rating"]

        # genre_ratings_to_join = genre_ratings[genre_ratings.year_month >=
        #                                      "201403"][genre_variables]

        movies_genre_ratings = movies_genre_gather.merge(
            genre_ratings, how="left")

        movies_genre_ratings_agg = movies_genre_ratings.groupby(["movieId", "year_month"]).mean()\
            .reset_index()

        return movies_genre_ratings_agg
