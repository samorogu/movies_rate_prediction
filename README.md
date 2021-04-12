# Prediction of movie ratings by users

The objective of the project is to predict whether a user will rate a movie as “high” or not. The definition of the response variable is:

- 1 in case the rating is >= 4 (flag for "high" rating)
- 0 in case the rating is <4

## Data

The dataset can be downloaded from [kaggle](https://www.kaggle.com/grouplens/movielens-20m-dataset)

## Notebooks

I recommend to open the notebooks from an IDE or an explorer that can render the notebooks because the graphs were made in plotly for interactivity.

### EDA

The first approach to the data is from EDA(exploratory data analysis) and this can be obtained from the EDA Notebooks:

- 01_movies.ipynb : In this notebook is the exploration of the rates of the movies across the time and the mean rating of the genres of the movies
- 02_tags.ipynb : In here you can find the cleaning with lemmatization and the most common words used by users for the movies
- 03_genome_tags.ipynb : For some tags there exist an importance on the subset of the movies. Because of data leakage(it is not clear what was the time this dataset was made), I don't incorporate it to the final model, but in here exist some explorations to some movies with this tags

### New Features

- 01_features_exploration.ipynb : I created features of lagging the rate of the movies, genres and users and incorporated a weighted mean rating for the tags that were used in the last 6 months on a movie

- 02_final_features : After having the new features, I created classes that generates the variables for movies, genres, users and tags that can be utilize on other notebooks to generate them again efficiently(this clases live in the code folder)

### Model and Conclusion

- 01_modeling.ipynb : In this notebook I incorporate a lgbm model, explain the most important variables and give a conclusion on the next steps to improve the model
