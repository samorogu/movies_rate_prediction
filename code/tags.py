import pandas as pd
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


class Tags(object):
    """A tag class that generates the tags variables"""

    def __init__(self, df_tags: pd.DataFrame, df_ratings: pd.DataFrame):
        self.tags_df = self.create_tags_history_rating(df_tags, df_ratings)

    def create_tags_history_rating(self, tag, ratings):
        """given a rating dataframe and tag dataframe, agregate the ratings of users to movies that recieved
        certain tags and weight them for the users that used them
        """
        tags_ratings = tag.loc[:, ~tag.columns.isin(["userId", "timestamp", "tag"])].drop_duplicates()\
            .merge(ratings, "left")

        tags_ratings_agg = tags_ratings.groupby(["processed_tag", "year_month"]).agg({"userId": "count", "rating": "mean"})\
            .reset_index()

        tags_ratings_agg.columns = [
            "processed_tag", "year_month", "count", "rating"]

        tags_ratings_agg_notNull = tags_ratings_agg.loc[tags_ratings_agg.rating.notnull(
        )]

        unique_cleaned_tags = tags_ratings_agg_notNull.processed_tag.drop_duplicates(
        ).reset_index(drop=True)
        unique_year_months = tags_ratings_agg_notNull.year_month.drop_duplicates(
        ).reset_index(drop=True)

        df1 = pd.DataFrame({'processed_tag': unique_cleaned_tags})
        df2 = pd.DataFrame({'year_month': unique_year_months})
        df1['tmp'] = 1
        df2['tmp'] = 1
        df_complete_history_tags = df1.merge(df2)

        tags_ratings_agg_notNull_full = df_complete_history_tags.merge(tags_ratings_agg_notNull,
                                                                       "left").fillna(0.0001).sort_values(
            by=['processed_tag', 'year_month']).reset_index(drop=True)

        tags_ratings_agg_notNull_full["last_1_months_tag_rating"] = tags_ratings_agg_notNull_full.groupby("processed_tag")["rating"]\
            .shift(1)\
            .reset_index()["rating"]

        tags_ratings_agg_notNull_full["last_1_months_tag_count"] = tags_ratings_agg_notNull_full.groupby("processed_tag")["count"]\
            .shift(1)\
            .reset_index()["count"]

        def wm(x): return np.average(
            x, weights=tags_ratings_agg_notNull_full.loc[x.index, "last_1_months_tag_count"])

        tags_ratings_agg_notNull_full["last_6_months_weighted_rating"] = tags_ratings_agg_notNull_full\
            .groupby("processed_tag")["last_1_months_tag_rating"].rolling(6).apply(wm)\
            .reset_index()["last_1_months_tag_rating"]

        tags_ratings_agg_notNull_full["last_6_months_tag_count"] = tags_ratings_agg_notNull_full\
            .groupby("processed_tag")["last_1_months_tag_count"].rolling(6).sum()\
            .reset_index()["last_1_months_tag_count"]

        tags_ratings_agg_notNull_full.loc[tags_ratings_agg_notNull_full
                                          .last_6_months_weighted_rating <= 0.001, 'last_6_months_tag_weighted_rating'] = 0

        tags_ratings_agg_notNull_full['last_6_months_tag_weighted_rating'] = tags_ratings_agg_notNull_full['last_6_months_tag_weighted_rating']\
            .replace(to_replace=0.0, method='ffill')

        columns_tags = ["processed_tag", "year_month",
                        "last_6_months_weighted_rating", "last_6_months_tag_count"]
        tags_ratings_to_join = tags_ratings_agg_notNull_full[
            tags_ratings_agg_notNull_full["year_month"] >= 201403][columns_tags]

        tags_weighted_rating = tag[tag.year_month >= 201403].merge(
            tags_ratings_to_join, "left").fillna(0.0001)

        def wm(x): return np.average(
            x, weights=tags_weighted_rating.loc[x.index, "last_6_months_tag_count"])

        tags_weighted_rating_agg = tags_weighted_rating\
            .groupby(["movieId", "year_month"])\
            .agg(last_6_months_weighted_rating=("last_6_months_weighted_rating", wm))\
            .reset_index()

        tags_weighted_rating_agg["year_month"] = tags_weighted_rating_agg["year_month"].astype(
            str)

        return tags_weighted_rating_agg
