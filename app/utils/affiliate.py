"""
Affiliate URL generator + curated deals seeder.
"""
import hashlib
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlencode, urlparse, urljoin

from app.config import settings
from app.schemas.product import PlatformOut

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Affiliate link generation
# ---------------------------------------------------------------------------
def generate_amazon_affiliate_url(asin: str, partner_tag: Optional[str] = None) -> str:
    tag = partner_tag or settings.amazon_partner_tag
    params = urlencode({"tag": tag, "linkCode": "ogi", "th": "1", "psc": "1"})
    return f"https://www.amazon.in/dp/{asin}?{params}"


def generate_flipkart_affiliate_url(
    product_url: str, affiliate_id: Optional[str] = None
) -> str:
    aff_id = affiliate_id or "dealfinderapp"
    if "?" in product_url:
        return f"{product_url}&affid={aff_id}"
    return f"{product_url}?affid={aff_id}"


def build_redirect_url(
    platform: PlatformOut,
    product_id: str,
    deal_id: Optional[str] = None,
    product_url: Optional[str] = None,
) -> str:
    """
    Build the internal /redirect/:id URL that tracks the click then forwards.
    """
    token = deal_id or product_id
    return f"{settings.base_url}/api/v1/redirect/{token}"


# ---------------------------------------------------------------------------
# Curated deals for the Deals screen (seeded into DB on startup)
# ---------------------------------------------------------------------------
CURATED_DEALS = [
    {
        "title": "Sony WH-1000XM5 Wireless NC Headphones",
        "description": "Industry-leading noise cancellation with 30h battery life. Best price ever on Amazon.",
        "category": "audio",
        "platform": "amazon",
        "deal_price": 24990.0,
        "original_price": 34990.0,
        "brand": "Sony",
        "rating": 4.7,
        "reviews_count": 28400,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/61kLLmJN2EL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B09XS7JWHH",
        "amazon_asin": "B09XS7JWHH",
        "priority": 10,
    },
    {
        "title": "Samsung 55\" 4K QLED Smart TV",
        "description": "Quantum HDR, Dolby Atmos, 144Hz gaming mode. Lowest price on Flipkart.",
        "category": "tvs",
        "platform": "flipkart",
        "deal_price": 49990.0,
        "original_price": 85990.0,
        "brand": "Samsung",
        "rating": 4.5,
        "reviews_count": 5400,
        "is_flash_deal": True,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/television/m/r/8/-original-imagfzg3pnhxvjax.jpeg",
        "product_url": "https://www.flipkart.com/samsung-55-qled-4k-tv-qn90d/p/",
        "flipkart_id": "TVSG8X2ZQPFHM7ND",
        "priority": 9,
        "flash_duration_hours": 8,
    },
    {
        "title": "Apple AirPods Pro (2nd Gen) USB-C",
        "description": "Active Noise Cancellation, Transparency mode, Personalized Spatial Audio.",
        "category": "audio",
        "platform": "amazon",
        "deal_price": 19900.0,
        "original_price": 24900.0,
        "brand": "Apple",
        "rating": 4.6,
        "reviews_count": 32100,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B09JQS53KZ",
        "amazon_asin": "B09JQS53KZ",
        "priority": 8,
    },
    {
        "title": "Apple iPhone 15 128GB",
        "description": "Dynamic Island, 48MP camera, A16 Bionic. Incredible deal on Amazon.",
        "category": "mobiles",
        "platform": "amazon",
        "deal_price": 59999.0,
        "original_price": 79900.0,
        "brand": "Apple",
        "rating": 4.6,
        "reviews_count": 18420,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CHX3QKBN",
        "amazon_asin": "B0CHX3QKBN",
        "priority": 8,
    },
    {
        "title": "Samsung Galaxy S24 FE 5G 128GB",
        "description": "Galaxy AI features, ProVisual camera, 6.7-inch AMOLED. Hot deal.",
        "category": "mobiles",
        "platform": "flipkart",
        "deal_price": 36999.0,
        "original_price": 57999.0,
        "brand": "Samsung",
        "rating": 4.3,
        "reviews_count": 9800,
        "is_flash_deal": False,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/b/g/k/-original-imagj5grxsmhvfhq.jpeg",
        "product_url": "https://www.flipkart.com/samsung-galaxy-s24-fe-graphite-128-gb/p/itm123abc456",
        "flipkart_id": "MOBGWZG5ZTEPSNKD",
        "priority": 7,
    },
    {
        "title": "Apple MacBook Air M2 13\" 256GB",
        "description": "18-hour battery, 8-core GPU, Liquid Retina display. Best-in-class laptop.",
        "category": "laptops",
        "platform": "amazon",
        "deal_price": 94990.0,
        "original_price": 114900.0,
        "brand": "Apple",
        "rating": 4.8,
        "reviews_count": 16200,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0BLKRXHSF",
        "amazon_asin": "B0BLKRXHSF",
        "priority": 8,
    },
    {
        "title": "boAt Airdopes 141 v2 Bluetooth Earbuds",
        "description": "42H playtime, ENx tech for clear calls, IPX4 water resistant.",
        "category": "audio",
        "platform": "amazon",
        "deal_price": 899.0,
        "original_price": 1999.0,
        "brand": "boAt",
        "rating": 4.1,
        "reviews_count": 84200,
        "is_flash_deal": True,
        "image_url": "https://m.media-amazon.com/images/I/61rBNl6BIOL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0BSJLQ2PP",
        "amazon_asin": "B0BSJLQ2PP",
        "priority": 6,
        "flash_duration_hours": 12,
    },
    {
        "title": "LG 55\" 4K OLED evo Smart TV",
        "description": "Perfect blacks, a9 AI Processor 4K Gen6, webOS 23. Cinema-grade picture.",
        "category": "tvs",
        "platform": "flipkart",
        "deal_price": 84990.0,
        "original_price": 169990.0,
        "brand": "LG",
        "rating": 4.7,
        "reviews_count": 3500,
        "is_flash_deal": False,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/television/m/d/h/-original-imagz6g4pnqbxkfh.jpeg",
        "product_url": "https://www.flipkart.com/lg-55-oled-c3-4k-tv/p/",
        "flipkart_id": "TVSLG9ZXBNMQ8KTF",
        "priority": 7,
    },
    {
        "title": "OnePlus 13 5G 512GB Arctic Dawn",
        "description": "Snapdragon 8 Elite, Hasselblad cameras, 100W SuperVOOC charging.",
        "category": "mobiles",
        "platform": "amazon",
        "deal_price": 69999.0,
        "original_price": 69999.0,
        "brand": "OnePlus",
        "rating": 4.6,
        "reviews_count": 14500,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/81Y1RA0rMJL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0DFJQHSHX",
        "amazon_asin": "B0DFJQHSHX",
        "priority": 6,
    },
    {
        "title": "ASUS ROG Strix G16 Gaming Laptop RTX 4070",
        "description": "Intel i9-14900HX, 16GB DDR5, 1TB NVMe. Dominate every game.",
        "category": "laptops",
        "platform": "amazon",
        "deal_price": 149990.0,
        "original_price": 189990.0,
        "brand": "ASUS",
        "rating": 4.5,
        "reviews_count": 3400,
        "is_flash_deal": False,
        "image_url": "https://m.media-amazon.com/images/I/81YHJNbkRdL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CQFBST3K",
        "amazon_asin": "B0CQFBST3K",
        "priority": 5,
    },
]


def build_deal_record(d: dict) -> dict:
    """Convert curated deal dict to a DB-compatible dict."""
    now = datetime.now(timezone.utc)
    platform = d["platform"]

    if platform == "amazon":
        asin = d.get("amazon_asin", "")
        affiliate_url = generate_amazon_affiliate_url(asin)
    else:
        affiliate_url = generate_flipkart_affiliate_url(d.get("product_url", ""))

    discount_pct = None
    savings_amount = None
    if d.get("original_price") and d["original_price"] > d["deal_price"]:
        savings_amount = round(d["original_price"] - d["deal_price"], 2)
        discount_pct = round(
            (savings_amount / d["original_price"]) * 100, 1
        )

    end_at = None
    if d.get("is_flash_deal") and d.get("flash_duration_hours"):
        end_at = now + timedelta(hours=d["flash_duration_hours"])

    return {
        "id": str(uuid.uuid4()),
        "product_id": str(uuid.uuid4()),  # placeholder; real seeder links to Product
        "title": d["title"],
        "description": d.get("description"),
        "category": d["category"],
        "platform": platform,
        "deal_price": d["deal_price"],
        "original_price": d.get("original_price"),
        "discount_pct": discount_pct,
        "savings_amount": savings_amount,
        "affiliate_url": affiliate_url,
        "image_url": d.get("image_url"),
        "brand": d.get("brand"),
        "rating": d.get("rating"),
        "reviews_count": d.get("reviews_count"),
        "is_flash_deal": d.get("is_flash_deal", False),
        "priority": d.get("priority", 0),
        "end_at": end_at.isoformat() if end_at else None,
    }
