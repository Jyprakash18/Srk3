import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

AMAZON_RE = re.compile(
    r"https?://(?:www\.)?amazon\.[a-z.]+/(?:[^\s]+)?(?:dp|gp/product)/([A-Z0-9]{10})",
    re.I
)


def find_amazon_links(text: str):
    if not text:
        return []
    return re.findall(r"https?://[^\s]+amazon\.[^\s]+", text)


def extract_asin(url: str):
    match = AMAZON_RE.search(url)
    return match.group(1) if match else None


def convert_link(url: str, tag: str):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["tag"] = [tag]
    clean_query = urlencode(query, doseq=True)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        clean_query,
        parsed.fragment
    ))


def get_product_info(url: str):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.find(id="productTitle")
        title = title.get_text(strip=True) if title else "Amazon Product"

        image = soup.find(id="landingImage")
        image_url = image.get("src") if image else None

        return title, image_url
    except Exception:
        return "Amazon Product", None
