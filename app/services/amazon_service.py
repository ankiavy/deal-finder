"""
Amazon Product Advertising API 5.0 service.
In production, swap USE_MOCK_DATA=false and fill in real credentials.
Mock data mirrors the normalized schema used by the matching engine.
"""
import logging
import asyncio
from typing import List, Optional
from app.schemas.product import PlatformProduct, PlatformOut, CategoryOut
from app.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Rich mock catalogue — realistic Indian market prices (INR)
# ---------------------------------------------------------------------------
_MOCK_PRODUCTS: List[dict] = [
    # -------- Mobiles --------
    {
        "product_id": "B0CHX3QKBN",
        "name": "Apple iPhone 15 (128 GB) - Black",
        "brand": "Apple",
        "model_number": "iPhone 15 128GB",
        "price": 59999.0,
        "mrp": 79900.0,
        "rating": 4.6,
        "reviews_count": 18420,
        "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CHX3QKBN",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["iphone 15", "apple iphone", "iphone 128gb"],
    },
    {
        "product_id": "B0CHX1FXJB",
        "name": "Apple iPhone 15 (256 GB) - Blue Titanium",
        "brand": "Apple",
        "model_number": "iPhone 15 256GB",
        "price": 69999.0,
        "mrp": 89900.0,
        "rating": 4.7,
        "reviews_count": 9840,
        "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CHX1FXJB",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["iphone 15 256", "apple iphone 256gb"],
    },
    {
        "product_id": "B0CHX4DCRN",
        "name": "Apple iPhone 15 Plus (128 GB) - Yellow",
        "brand": "Apple",
        "model_number": "iPhone 15 Plus 128GB",
        "price": 74999.0,
        "mrp": 89900.0,
        "rating": 4.5,
        "reviews_count": 5210,
        "image_url": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CHX4DCRN",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["iphone 15 plus", "apple iphone plus"],
    },
    {
        "product_id": "B0CM5JV5GK",
        "name": "Samsung Galaxy S24 FE 5G (128 GB, 8 GB RAM) - Graphite",
        "brand": "Samsung",
        "model_number": "Galaxy S24 FE 128GB",
        "price": 37499.0,
        "mrp": 57999.0,
        "rating": 4.4,
        "reviews_count": 12300,
        "image_url": "https://m.media-amazon.com/images/I/71sKHqDKMNL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CM5JV5GK",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["samsung s24 fe", "galaxy s24", "samsung galaxy s24 fan edition"],
    },
    {
        "product_id": "B0C9P3KQZM",
        "name": "Samsung Galaxy S24+ 5G (256 GB, 12 GB RAM) - Cobalt Violet",
        "brand": "Samsung",
        "model_number": "Galaxy S24+ 256GB",
        "price": 74999.0,
        "mrp": 99999.0,
        "rating": 4.5,
        "reviews_count": 8700,
        "image_url": "https://m.media-amazon.com/images/I/71sKHqDKMNL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0C9P3KQZM",
        "is_prime": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["samsung s24 plus", "galaxy s24+", "samsung s24+"],
    },
    {
        "product_id": "B0DFJQHSHX",
        "name": "OnePlus 13 5G (512 GB, 16 GB RAM) - Arctic Dawn",
        "brand": "OnePlus",
        "model_number": "OnePlus 13 512GB",
        "price": 69999.0,
        "mrp": 69999.0,
        "rating": 4.6,
        "reviews_count": 14500,
        "image_url": "https://m.media-amazon.com/images/I/81Y1RA0rMJL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0DFJQHSHX",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["oneplus 13", "oneplus 13 5g", "oneplus flagship"],
    },
    {
        "product_id": "B0CP5K7T3V",
        "name": "Xiaomi 14 5G (512 GB, 12 GB RAM) - Jade Green",
        "brand": "Xiaomi",
        "model_number": "Xiaomi 14 512GB",
        "price": 59999.0,
        "mrp": 69999.0,
        "rating": 4.4,
        "reviews_count": 7800,
        "image_url": "https://m.media-amazon.com/images/I/71L9TFDzomL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CP5K7T3V",
        "is_prime": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["xiaomi 14", "mi 14"],
    },
    {
        "product_id": "B0B7NMXZ6J",
        "name": "Redmi Note 13 Pro+ 5G (256 GB, 12 GB RAM) - Aurora Purple",
        "brand": "Redmi",
        "model_number": "Redmi Note 13 Pro+ 256GB",
        "price": 29999.0,
        "mrp": 35999.0,
        "rating": 4.3,
        "reviews_count": 22100,
        "image_url": "https://m.media-amazon.com/images/I/71L9TFDzomL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0B7NMXZ6J",
        "is_prime": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["redmi note 13 pro plus", "redmi note 13 pro+", "redmi note 13"],
    },
    # -------- Laptops --------
    {
        "product_id": "B0BLKRXHSF",
        "name": "Apple MacBook Air 13 inch (M2 Chip, 8 GB RAM, 256 GB SSD) - Midnight",
        "brand": "Apple",
        "model_number": "MacBook Air M2 256GB",
        "price": 94990.0,
        "mrp": 114900.0,
        "rating": 4.8,
        "reviews_count": 16200,
        "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0BLKRXHSF",
        "is_prime": True,
        "delivery_days": 2,
        "category": "laptops",
        "keywords": ["macbook air m2", "macbook air 13", "apple laptop m2"],
    },
    {
        "product_id": "B0D4JKBRJH",
        "name": "Apple MacBook Pro 14 inch (M3 Pro, 18 GB RAM, 512 GB SSD) - Space Black",
        "brand": "Apple",
        "model_number": "MacBook Pro M3 Pro 512GB",
        "price": 199990.0,
        "mrp": 229900.0,
        "rating": 4.9,
        "reviews_count": 5300,
        "image_url": "https://m.media-amazon.com/images/I/71jG+e7roXL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0D4JKBRJH",
        "is_prime": True,
        "delivery_days": 2,
        "category": "laptops",
        "keywords": ["macbook pro m3", "macbook pro 14", "apple macbook pro"],
    },
    {
        "product_id": "B0CQFBST3K",
        "name": "ASUS ROG Strix G16 Gaming Laptop (Intel i9-14900HX, 16 GB, 1 TB SSD, RTX 4070)",
        "brand": "ASUS",
        "model_number": "ROG Strix G16 2024",
        "price": 149990.0,
        "mrp": 189990.0,
        "rating": 4.5,
        "reviews_count": 3400,
        "image_url": "https://m.media-amazon.com/images/I/81YHJNbkRdL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CQFBST3K",
        "is_prime": True,
        "delivery_days": 3,
        "category": "laptops",
        "keywords": ["asus rog strix g16", "rog gaming laptop", "asus rog rtx 4070"],
    },
    # -------- Audio --------
    {
        "product_id": "B09XS7JWHH",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones - Black",
        "brand": "Sony",
        "model_number": "WH-1000XM5",
        "price": 24990.0,
        "mrp": 34990.0,
        "rating": 4.7,
        "reviews_count": 28400,
        "image_url": "https://m.media-amazon.com/images/I/61kLLmJN2EL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B09XS7JWHH",
        "is_prime": True,
        "delivery_days": 1,
        "category": "audio",
        "keywords": ["sony wh-1000xm5", "sony headphones noise cancelling", "sony xm5"],
    },
    {
        "product_id": "B09JQS53KZ",
        "name": "Apple AirPods Pro (2nd Generation) with USB-C",
        "brand": "Apple",
        "model_number": "AirPods Pro 2nd Gen",
        "price": 19900.0,
        "mrp": 24900.0,
        "rating": 4.6,
        "reviews_count": 32100,
        "image_url": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B09JQS53KZ",
        "is_prime": True,
        "delivery_days": 1,
        "category": "audio",
        "keywords": ["airpods pro 2", "apple airpods pro", "airpods pro usb-c"],
    },
    {
        "product_id": "B0BSJLQ2PP",
        "name": "boAt Airdopes 141 v2 Bluetooth Earbuds",
        "brand": "boAt",
        "model_number": "Airdopes 141 v2",
        "price": 899.0,
        "mrp": 1999.0,
        "rating": 4.1,
        "reviews_count": 84200,
        "image_url": "https://m.media-amazon.com/images/I/61rBNl6BIOL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0BSJLQ2PP",
        "is_prime": True,
        "delivery_days": 2,
        "category": "audio",
        "keywords": ["boat airdopes 141", "boat earbuds", "boat airdopes"],
    },
    # -------- TVs --------
    {
        "product_id": "B0CG97V2X4",
        "name": "Samsung 55 inch 4K Ultra HD Smart QLED TV (QA55QN90DAKLXL)",
        "brand": "Samsung",
        "model_number": "QA55QN90D",
        "price": 84990.0,
        "mrp": 164900.0,
        "rating": 4.4,
        "reviews_count": 6800,
        "image_url": "https://m.media-amazon.com/images/I/71yx1FLrMfL._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CG97V2X4",
        "is_prime": True,
        "delivery_days": 3,
        "category": "tvs",
        "keywords": ["samsung 55 inch qled", "samsung 4k qled tv", "samsung qled 55"],
    },
    {
        "product_id": "B0CF89PY75",
        "name": "LG 55 inch 4K OLED Smart TV (OLED55C3PSA)",
        "brand": "LG",
        "model_number": "OLED55C3",
        "price": 109999.0,
        "mrp": 169990.0,
        "rating": 4.7,
        "reviews_count": 4200,
        "image_url": "https://m.media-amazon.com/images/I/71ZEqX0Ec3L._SX679_.jpg",
        "product_url": "https://www.amazon.in/dp/B0CF89PY75",
        "is_prime": True,
        "delivery_days": 4,
        "category": "tvs",
        "keywords": ["lg 55 oled", "lg oled c3", "lg oled tv 55"],
    },
]


def _match_query(query: str, product: dict) -> bool:
    """Simple keyword matching for mock search."""
    q = query.lower()
    name_lower = product["name"].lower()
    # Direct substring match
    if q in name_lower:
        return True
    # Keyword match
    for kw in product.get("keywords", []):
        if q in kw or kw in q:
            return True
    # Word overlap match
    q_words = set(q.split())
    name_words = set(name_lower.split())
    overlap = q_words & name_words
    return len(overlap) >= 1 and len(q_words) > 0


class AmazonService:
    """
    Production: calls Amazon PAAPI 5.0 with AWS SigV4 auth.
    Development: returns mock data.
    """

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> List[PlatformProduct]:
        if settings.use_mock_data:
            return await self._mock_search(query, category, limit)
        return await self._real_search(query, category, limit)

    async def _mock_search(
        self, query: str, category: Optional[str], limit: int
    ) -> List[PlatformProduct]:
        await asyncio.sleep(0.05)  # simulate network latency
        results = []
        for p in _MOCK_PRODUCTS:
            if category and p.get("category") != category:
                continue
            if not _match_query(query, p):
                continue

            # Slightly vary prices to simulate dynamic pricing
            import random
            price_variation = random.uniform(0.97, 1.03)
            varied_price = round(p["price"] * price_variation, -1)

            results.append(
                PlatformProduct(
                    platform=PlatformOut.AMAZON,
                    product_id=p["product_id"],
                    name=p["name"],
                    brand=p.get("brand"),
                    model_number=p.get("model_number"),
                    price=varied_price,
                    mrp=p.get("mrp"),
                    rating=p.get("rating"),
                    reviews_count=p.get("reviews_count"),
                    image_url=p.get("image_url"),
                    product_url=p["product_url"],
                    is_prime=p.get("is_prime", False),
                    delivery_days=p.get("delivery_days"),
                    category=CategoryOut(p["category"]) if p.get("category") else None,
                )
            )
            if len(results) >= limit:
                break

        return results

    async def _real_search(
        self, query: str, category: Optional[str], limit: int
    ) -> List[PlatformProduct]:
        """
        Real Amazon PAAPI 5.0 implementation.
        Requires: amazon_access_key, amazon_secret_key, amazon_partner_tag
        Uses AWS SigV4 request signing.
        Install: pip install amazon-paapi5
        """
        raise NotImplementedError(
            "Real Amazon API integration requires credentials. "
            "Set USE_MOCK_DATA=false and fill .env with Amazon credentials."
        )
