from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

books = pd.read_csv("books.csv", sep=";", encoding="latin-1", on_bad_lines="skip")
ratings = pd.read_csv("ratings.csv", sep=";", encoding="latin-1", on_bad_lines="skip")

books = books[["ISBN", "Book-Title", "Book-Author", "Image-URL-L"]]
books.columns = ["isbn", "title", "author", "image"]

ratings.columns = ["user_id", "isbn", "rating"]

data = ratings.merge(books, on="isbn")

popular = data.groupby(["title", "author", "image"]).agg(
    rating_count=("rating", "count"),
    avg_rating=("rating", "mean")
).reset_index()

popular = popular.sort_values(["rating_count", "avg_rating"], ascending=False).head(36)

def make_books(df, tag="Popular"):
    result = []
    for _, row in df.iterrows():
        rating = row["avg_rating"] if "avg_rating" in row else 0

        result.append({
            "title": str(row["title"]),
            "author": str(row["author"]),
            "image": str(row["image"]),
            "rating": round(float(rating), 1),
            "tag": tag,
            "description": f"{row['title']} by {row['author']} is recommended based on reader ratings, popularity, and user interest."
        })
    return result

@app.route("/", methods=["GET", "POST"])
def home():
    search_results = []
    search_text = ""

    if request.method == "POST":
        search_text = request.form.get("book", "").strip()

        searched_books = books[
            books["title"].str.contains(search_text, case=False, na=False) |
            books["author"].str.contains(search_text, case=False, na=False)
        ].drop_duplicates("title").head(18)

        book_ratings = data.groupby("title")["rating"].mean().reset_index()
        book_ratings.columns = ["title", "avg_rating"]

        searched_books = searched_books.merge(book_ratings, on="title", how="left")
        searched_books["avg_rating"] = searched_books["avg_rating"].fillna(0)

        search_results = make_books(searched_books, "Search Result")

    hero_book = make_books(popular.head(1), "Featured")[0]
    trending = make_books(popular.head(12), "Trending")
    top_rated = make_books(popular.sort_values("avg_rating", ascending=False).head(12), "Top Rated")
    recommended = make_books(popular.sample(min(12, len(popular)), random_state=7), "Recommended")

    return render_template(
        "index.html",
        hero_book=hero_book,
        search_results=search_results,
        trending=trending,
        top_rated=top_rated,
        recommended=recommended,
        search_text=search_text
    )

if __name__ == "__main__":
    app.run(debug=True)