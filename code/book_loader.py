# book_loader.py — Download and clean Project Gutenberg books

import requests
import re
import os

def download_book(url: str) -> str:

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Try multiple Gutenberg formats
    if "gutenberg" in url:

        book_id_match = re.findall(r"\d+", url)

        if book_id_match:

            book_id = book_id_match[0]

            possible_urls = [

                f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",

                f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",

                f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt",

                url
            ]

            for u in possible_urls:

                try:

                    response = requests.get(
                        u,
                        headers=headers,
                        timeout=20
                    )

                    if response.status_code == 200:

                        url = u
                        break

                except:
                    pass

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    text = response.content.decode(
        response.apparent_encoding or "utf-8",
        errors="replace"
    )
    if "<html" in text.lower():

        raise Exception(
            "HTML version detected. Choose another format."
        )

    text = _strip_gutenberg_header(text)

    text = _strip_gutenberg_footer(text)

    text = _clean_text(text)

    if len(text) < 1000:
        raise Exception("Book text too small")
    
    # Save the full book text to a file for reading
    try:
        os.makedirs("books", exist_ok=True)
        book_id = re.findall(r"\d+", url)[0] if re.findall(r"\d+", url) else "unknown"
        book_title = re.sub(r'[^\w\s-]', '', url.split('/')[-1].replace('.txt', ''))[:50]
        book_path = f"books/{book_id}_{book_title}.txt"
        with open(book_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Warning: Could not save book file: {e}")
    
    return text


def get_book_text(book_id: str, max_chars: int = None) -> str:
    """
    Get the full book text by book ID.
    """
    try:
        # Find the book file
        books_dir = "books"
        if not os.path.exists(books_dir):
            return None
            
        for filename in os.listdir(books_dir):
            if filename.startswith(book_id):
                with open(os.path.join(books_dir, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                    if max_chars:
                        return text[:max_chars]
                    return text
    except Exception as e:
        print(f"Error reading book: {e}")
    
    return None


def get_book_text_by_url(url: str, max_chars: int = 5000) -> str:
    """Get saved book text by its source URL (looks up book_id from URL)."""
    try:
        book_id_match = re.findall(r"\d+", url)
        if not book_id_match:
            return None
        book_id = book_id_match[0]
        return get_book_text(book_id, max_chars=max_chars)
    except Exception:
        return None


def get_book_by_url(url: str) -> tuple:
    """
    Download a book and return (text, book_path, book_id)
    """
    text = download_book(url)
    book_id = re.findall(r"\d+", url)[0] if re.findall(r"\d+", url) else "unknown"
    return text, book_id


def _strip_gutenberg_header(text: str) -> str:
    """Remove the Gutenberg header that appears before the actual book."""
    patterns = [
        r"\*\*\* START OF (THE|THIS) PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\*START OF (THE|THIS) PROJECT GUTENBERG EBOOK .+?\*\*\*",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return text[match.end():]
    return text


def _strip_gutenberg_footer(text: str) -> str:
    """Remove the Gutenberg footer that appears after the actual book."""
    patterns = [
        r"\*\*\* END OF (THE|THIS) PROJECT GUTENBERG EBOOK .+? \*\*\*",
        r"\*\*\*END OF (THE|THIS) PROJECT GUTENBERG EBOOK .+?\*\*\*",
        r"End of (the )?Project Gutenberg",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text[:match.start()]
    return text


def _clean_text(text: str) -> str:
    """Normalize whitespace and remove junk characters."""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace per line
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip()


def estimate_reading_time(text: str) -> str:
    """Estimate reading time at 200 words/minute."""
    words = len(text.split())
    minutes = words // 200
    if minutes < 60:
        return f"~{minutes} min read"
    hours = minutes // 60
    mins = minutes % 60
    return f"~{hours}h {mins}m read"


def get_pdf_url(url):

    if "gutenberg" in url:

        book_id = url.split("/")[-1].split(".")[0]

        return f"https://www.gutenberg.org/files/{book_id}/{book_id}-pdf.pdf"

    return None