"""
Catalog scraper — downloads product images from publicly accessible retailer pages.

Usage:
    python scripts/scrape_catalog.py                  # scrape all retailers
    python scripts/scrape_catalog.py --retailer hm    # scrape H&M only
    python scripts/scrape_catalog.py --max 50         # limit to 50 images per retailer

Rules followed:
  - Checks robots.txt before scraping each domain
  - 1–2 second random delay between every request
  - Max ~100 images per retailer (configurable)
  - Identifies as an academic project in the User-Agent
"""

import argparse
import hashlib
import io
import json
import random
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from PIL import Image


OUTPUT_DIR = Path("data/catalog_images/scraped")
DEFAULT_MAX = 100
DELAY_RANGE = (1.0, 2.0)  # seconds between requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AcademicCapstoneBot/1.0; "
        "fashion retrieval class project)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── Retailer configurations ────────────────────────────────────────────────
RETAILERS = {
    "hm": {
        "name": "H&M",
        "base_url": "https://www2.hm.com",
        "category_urls": [
            "https://www2.hm.com/en_us/men/products/jackets-and-coats.html",
            "https://www2.hm.com/en_us/men/products/shirts.html",
            "https://www2.hm.com/en_us/men/products/hoodies-and-sweatshirts.html",
            "https://www2.hm.com/en_us/women/products/jackets-and-coats.html",
            "https://www2.hm.com/en_us/women/products/shirts-and-blouses.html",
            "https://www2.hm.com/en_us/women/products/hoodies-and-sweatshirts.html",
        ],
        "scrape_fn": "scrape_hm",
    },
    "uniqlo": {
        "name": "Uniqlo",
        "base_url": "https://www.uniqlo.com",
        "api_urls": [
            "https://www.uniqlo.com/us/api/commerce/v5/en/products?path=%2Fmen%2Ftops%2Ft-shirts&offset=0&limit=36&httpFailure=true",
            "https://www.uniqlo.com/us/api/commerce/v5/en/products?path=%2Fmen%2Foutwear&offset=0&limit=36&httpFailure=true",
            "https://www.uniqlo.com/us/api/commerce/v5/en/products?path=%2Fwomen%2Ftops%2Ft-shirts&offset=0&limit=36&httpFailure=true",
            "https://www.uniqlo.com/us/api/commerce/v5/en/products?path=%2Fwomen%2Foutwear&offset=0&limit=36&httpFailure=true",
        ],
        "scrape_fn": "scrape_uniqlo",
    },
}


# ── robots.txt helper ──────────────────────────────────────────────────────
_robots_cache = {}

def can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    if robots_url not in _robots_cache:
        rp = RobotFileParser()
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            # If robots.txt is unreachable, allow by default
            _robots_cache[robots_url] = None
            return True
        _robots_cache[robots_url] = rp
    rp = _robots_cache[robots_url]
    if rp is None:
        return True
    return rp.can_fetch(HEADERS["User-Agent"], url)


def polite_get(url: str, **kwargs) -> requests.Response | None:
    """GET with rate limiting and robots.txt check."""
    if not can_fetch(url):
        print(f"  [robots.txt] Blocked: {url}")
        return None
    time.sleep(random.uniform(*DELAY_RANGE))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, **kwargs)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return None


# ── Image download helper ──────────────────────────────────────────────────
def download_image(url: str, retailer: str) -> Path | None:
    """Download an image, save to OUTPUT_DIR/<retailer>/, return saved path."""
    dest_dir = OUTPUT_DIR / retailer
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Use a hash of the URL as filename to avoid duplicates
    ext = Path(urlparse(url).path).suffix.lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    fname = hashlib.md5(url.encode()).hexdigest()[:16] + ext
    dest = dest_dir / fname

    if dest.exists():
        return dest  # already downloaded

    resp = polite_get(url)
    if resp is None:
        return None

    try:
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        # Skip tiny images (icons, thumbnails < 100px)
        if img.width < 100 or img.height < 100:
            return None
        img.save(dest)
        return dest
    except Exception as e:
        print(f"  [image error] {url}: {e}")
        return None


# ── H&M scraper ────────────────────────────────────────────────────────────
def scrape_hm(config: dict, max_items: int) -> list[Path]:
    saved = []
    for page_url in config["category_urls"]:
        if len(saved) >= max_items:
            break
        print(f"\n  Fetching {page_url}")
        resp = polite_get(page_url)
        if resp is None:
            continue

        soup = BeautifulSoup(resp.text, "lxml")

        # H&M embeds product JSON in a <script> tag
        image_urls = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                # ItemList or Product schema
                if isinstance(data, dict) and data.get("@type") == "ItemList":
                    for item in data.get("itemListElement", []):
                        img = item.get("item", {}).get("image")
                        if img:
                            image_urls.append(img if img.startswith("http") else "https:" + img)
                elif isinstance(data, dict) and data.get("image"):
                    img = data["image"]
                    image_urls.append(img if img.startswith("http") else "https:" + img)
            except Exception:
                continue

        # Fallback: look for product image tags
        if not image_urls:
            for img_tag in soup.select("img.item-image, img[class*='product'], img[data-src*='hm.com']"):
                src = img_tag.get("src") or img_tag.get("data-src") or ""
                if "hm.com" in src or src.startswith("//"):
                    if src.startswith("//"):
                        src = "https:" + src
                    image_urls.append(src)

        print(f"  Found {len(image_urls)} image URLs")
        for url in image_urls:
            if len(saved) >= max_items:
                break
            # Request a larger image size variant
            url = url.replace("&call=url[file:/product/main]", "")
            path = download_image(url, "hm")
            if path:
                saved.append(path)
                print(f"  [{len(saved)}/{max_items}] Saved {path.name}")

    return saved


# ── Uniqlo scraper (JSON API) ──────────────────────────────────────────────
def scrape_uniqlo(config: dict, max_items: int) -> list[Path]:
    saved = []
    for api_url in config["api_urls"]:
        if len(saved) >= max_items:
            break
        print(f"\n  Fetching {api_url}")
        resp = polite_get(api_url)
        if resp is None:
            continue

        try:
            data = resp.json()
        except Exception:
            print("  [error] Could not parse JSON")
            continue

        products = data.get("result", {}).get("items", [])
        print(f"  Found {len(products)} products")

        for product in products:
            if len(saved) >= max_items:
                break
            # Uniqlo image URL pattern
            product_id = product.get("productId", "")
            if not product_id:
                continue
            img_url = f"https://image.uniqlo.com/UQ/ST3/us/imagesgoods/{product_id}/item/usgoods_01_main.jpg?width=600"
            path = download_image(img_url, "uniqlo")
            if path:
                saved.append(path)
                print(f"  [{len(saved)}/{max_items}] Saved {path.name}")

    return saved


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Scrape retailer catalog images")
    parser.add_argument("--retailer", choices=list(RETAILERS.keys()), help="Scrape one retailer only")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, help="Max images per retailer")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = {args.retailer: RETAILERS[args.retailer]} if args.retailer else RETAILERS

    total = 0
    for key, config in targets.items():
        print(f"\n{'='*50}")
        print(f"Scraping {config['name']} (max {args.max} images)")
        print(f"{'='*50}")

        scrape_fn = globals()[config["scrape_fn"]]
        saved = scrape_fn(config, args.max)
        total += len(saved)
        print(f"\n  Done: {len(saved)} images saved for {config['name']}")

    print(f"\nTotal images downloaded: {total}")
    print(f"Saved to: {OUTPUT_DIR.resolve()}")
    print("\nNext step: delete artifacts/ and run 'streamlit run app.py' to rebuild the catalog index.")


if __name__ == "__main__":
    main()
