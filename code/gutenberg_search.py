# gutenberg_search.py — Search Project Gutenberg via Gutendex API

import requests


def search_gutenberg(query: str, max_results: int = 6) -> list[dict]:
    """
    Search Project Gutenberg for books matching the query.
    Returns a list of dicts with title, author, year, genre, and url.
    """
    try:
        url = f"https://gutendex.com/books/?search={requests.utils.quote(query)}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return []

    results = []

    for book in data.get("results", [])[:max_results]:

        title = book.get("title", "Unknown Title")

        # Author
        authors = book.get("authors", [])
        author = authors[0]["name"] if authors else "Unknown Author"

        # Year — from birth/death is not available, use download count as proxy
        # Gutendex doesn't return year directly
        subjects = book.get("subjects", [])
        genre = _guess_genre(subjects, title)

        # Find best plain text URL
        formats = book.get("formats", {})
        text_url = _get_text_url(formats)

        if not text_url:
            continue  # Skip books without a text URL

        # Cover image
        cover = formats.get("image/jpeg", None)

        results.append({
            "title": title,
            "author": author,
            "year": "",
            "genre": genre,
            "emoji": _genre_emoji(genre),
            "description": f"A Project Gutenberg classic by {author}.",
            "url": text_url,
            "cover": cover,
            "downloads": book.get("download_count", 0),
        })

    # Sort by download count (popularity)
    results.sort(key=lambda x: x["downloads"], reverse=True)

    return results


def _get_text_url(formats):

    # Only UTF-8 text

    for key in formats:

        if "text/plain; charset=utf-8" in key.lower():

            return formats[key]

    # fallback

    for key in formats:

        if "text/plain" in key.lower():

            return formats[key]

    return None


def _guess_genre(subjects: list, title: str) -> str:
    """Heuristically guess genre from subjects list."""
    joined = " ".join(subjects).lower() + " " + title.lower()

    if any(w in joined for w in ["detective", "mystery", "crime", "murder", "sherlock"]):
        return "Mystery"
    if any(w in joined for w in ["horror", "ghost", "vampire", "monster", "gothic"]):
        return "Horror"
    if any(w in joined for w in ["adventure", "sea", "island", "pirate", "voyage"]):
        return "Adventure"
    if any(w in joined for w in ["science fiction", "war of the worlds", "time machine", "mars"]):
        return "Sci-Fi"
    if any(w in joined for w in ["romance", "love", "marriage", "austen"]):
        return "Romance"
    if any(w in joined for w in ["satire", "humor", "comedy", "wit"]):
        return "Satire"
    if any(w in joined for w in ["philosophy", "moral", "ethics"]):
        return "Philosophical"
    if any(w in joined for w in ["myth", "legend", "greek", "roman", "gods"]):
        return "Mythology"
    if any(w in joined for w in ["drama", "society", "social", "dickens"]):
        return "Drama"
    return "Classic"


def _genre_emoji(genre: str) -> str:
    mapping = {
        "Mystery": "🔍",
        "Horror": "🕯️",
        "Adventure": "🌍",
        "Sci-Fi": "🚀",
        "Romance": "💌",
        "Satire": "😏",
        "Philosophical": "🪞",
        "Mythology": "🌀",
        "Drama": "🎭",
        "Classic": "📖",
    }
    return mapping.get(genre, "📖")