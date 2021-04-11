import pandas as pd

from movies import Movies


class Users(object):
    """A users class"""

    def __init__(self, df_ratings: pd.DataFrame):
        self.users_df = self.create_users_history_rating(df_ratings)

    def create_users_history_rating(self, user_ratings):
        user_ratings_agg = user_ratings.groupby(["userId", "year_month"]).agg(count=("userId", "count"),
                                                                              mean_rating=("rating", "mean")).reset_index()

        user_ratings_agg["last_1_months_user_rating"] = user_ratings_agg.groupby("userId")['mean_rating'].shift(1)\
            .reset_index()["mean_rating"]
        user_ratings_agg["last_1_months_user_rating_counts"] = user_ratings_agg.groupby("userId")['count'].shift(1)\
            .reset_index()["count"]
        user_ratings_agg["mean_3_months_user_rating"] = user_ratings_agg.groupby("userId")['last_1_months_user_rating'].rolling(3).mean()\
            .reset_index()["last_1_months_user_rating"]
        user_ratings_agg["mean_6_months_user_rating"] = user_ratings_agg.groupby("userId")['last_1_months_user_rating'].rolling(6).mean()\
            .reset_index()["last_1_months_user_rating"]
        user_ratings_agg["last_1_month_per_3_months_user_rating"] = user_ratings_agg.last_1_months_user_rating / \
            user_ratings_agg.mean_3_months_user_rating
        user_ratings_agg["last_1_month_per_6_months_user_rating"] = user_ratings_agg.last_1_months_user_rating / \
            user_ratings_agg.mean_6_months_user_rating

        return user_ratings_agg
