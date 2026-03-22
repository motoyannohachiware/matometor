import urllib.request
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")


def search_by_isbn(isbn):
    """ISBNでGoogle Books APIを検索して書誌情報を返す"""
    isbn = isbn.replace("-", "").strip()
    query = urllib.parse.urlencode({"q": f"isbn:{isbn}"})

    if API_KEY:
        url = f"https://www.googleapis.com/books/v1/volumes?{query}&key={API_KEY}"
    else:
        url = f"https://www.googleapis.com/books/v1/volumes?{query}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("totalItems", 0) == 0:
            return None

        item = data["items"][0]
        info = item.get("volumeInfo", {})

        title = info.get("title", "")
        authors = info.get("authors", [])
        author = "、".join(authors) if authors else None
        categories = info.get("categories", [])
        category = categories[0] if categories else None

        return {
            "title": title,
            "author": author,
            "category": category,
        }

    except Exception as e:
        print(f"Google Books APIエラー: {e}")
        return None