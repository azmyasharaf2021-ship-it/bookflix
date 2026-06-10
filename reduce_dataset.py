import pandas as pd

books = pd.read_csv("books.csv", sep=";", encoding="latin-1", on_bad_lines="skip")
ratings = pd.read_csv("ratings.csv", sep=";", encoding="latin-1", on_bad_lines="skip")

books_small = books.head(8000)
ratings_small = ratings.head(30000)

books_small.to_csv("books_small.csv", sep=";", index=False)
ratings_small.to_csv("ratings_small.csv", sep=";", index=False)

print("Small dataset created successfully")