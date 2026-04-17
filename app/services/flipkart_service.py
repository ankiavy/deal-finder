"""
Flipkart Affiliate API service.
Mock data deliberately uses the same products with slightly different prices
so the matching engine can compare across platforms.
"""
import logging
import asyncio
from typing import List, Optional
from app.schemas.product import PlatformProduct, PlatformOut, CategoryOut
from app.config import settings

logger = logging.getLogger(__name__)


_MOCK_PRODUCTS: List[dict] = [
    # -------- Mobiles (same SKUs, slight Flipkart price variation) --------
    {
        "product_id": "MOBGTAGPNAFAXX7E",
        "name": "Apple iPhone 15 (128GB) Black",
        "brand": "Apple",
        "model_number": "iPhone 15 128GB",
        "price": 61499.0,
        "mrp": 79900.0,
        "rating": 4.5,
        "reviews_count": 14200,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/v/j/b/-original-imaghx9qnhmhk9qn.jpeg",
        "product_url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4",
        "is_assured": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["iphone 15", "apple iphone", "iphone 128gb"],
    },
    {
        "product_id": "MOBGTAGQ5CZMXFCM",
        "name": "Apple iPhone 15 256GB Blue Titanium",
        "brand": "Apple",
        "model_number": "iPhone 15 256GB",
        "price": 67999.0,
        "mrp": 89900.0,
        "rating": 4.6,
        "reviews_count": 8400,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/v/j/b/-original-imaghx9qnhmhk9qn.jpeg",
        "product_url": "https://www.flipkart.com/apple-iphone-15-blue-256-gb/p/itm9ae3a66a81e30",
        "is_assured": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["iphone 15 256", "apple iphone 256gb"],
    },
    {
        "product_id": "MOBGTAGPNAFAXX8Y",
        "name": "Apple iPhone 15 Plus 128GB Yellow",
        "brand": "Apple",
        "model_number": "iPhone 15 Plus 128GB",
        "price": 75990.0,
        "mrp": 89900.0,
        "rating": 4.4,
        "reviews_count": 4100,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/v/j/b/-original-imaghx9qnhmhk9qn.jpeg",
        "product_url": "https://www.flipkart.com/apple-iphone-15-plus-yellow-128gb/p/",
        "is_assured": True,
        "delivery_days": 3,
        "category": "mobiles",
        "keywords": ["iphone 15 plus", "apple iphone plus"],
    },
    {
        "product_id": "MOBGWZG5ZTEPSNKD",
        "name": "Samsung Galaxy S24 FE 5G (8GB RAM, 128GB) - Graphite",
        "brand": "Samsung",
        "model_number": "Galaxy S24 FE 128GB",
        "price": 36999.0,
        "mrp": 57999.0,
        "rating": 4.3,
        "reviews_count": 9800,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/b/g/k/-original-imagj5grxsmhvfhq.jpeg",
        "product_url": "https://www.flipkart.com/samsung-galaxy-s24-fe-graphite-128-gb/p/itm123abc456",
        "is_assured": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["samsung s24 fe", "galaxy s24", "samsung galaxy s24 fan edition"],
    },
    {
        "product_id": "MOBGXZRK5PTGHNHB",
        "name": "Samsung Galaxy S24+ 5G (12GB RAM, 256GB) Cobalt Violet",
        "brand": "Samsung",
        "model_number": "Galaxy S24+ 256GB",
        "price": 76999.0,
        "mrp": 99999.0,
        "rating": 4.5,
        "reviews_count": 6200,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/b/g/k/-original-imagj5grxsmhvfhq.jpeg",
        "product_url": "https://www.flipkart.com/samsung-galaxy-s24-plus-cobalt-violet/p/",
        "is_assured": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["samsung s24 plus", "galaxy s24+", "samsung s24+"],
    },
    {
        "product_id": "MOBH2JZGHFVD7YBT",
        "name": "OnePlus 13 5G (16GB RAM, 512GB) Arctic Dawn",
        "brand": "OnePlus",
        "model_number": "OnePlus 13 512GB",
        "price": 69999.0,
        "mrp": 69999.0,
        "rating": 4.5,
        "reviews_count": 11200,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/q/7/3/-original-imagnbpevpnhfagk.jpeg",
        "product_url": "https://www.flipkart.com/oneplus-13-arctic-dawn-512gb/p/",
        "is_assured": True,
        "delivery_days": 1,
        "category": "mobiles",
        "keywords": ["oneplus 13", "oneplus 13 5g", "oneplus flagship"],
    },
    {
        "product_id": "MOBH1PZXKFVD8ZCU",
        "name": "Xiaomi 14 5G (12GB RAM, 512GB) Jade Green",
        "brand": "Xiaomi",
        "model_number": "Xiaomi 14 512GB",
        "price": 61499.0,
        "mrp": 69999.0,
        "rating": 4.3,
        "reviews_count": 5900,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/x/o/c/-original-imagnaqgh2hrjzqr.jpeg",
        "product_url": "https://www.flipkart.com/xiaomi-14-jade-green-512gb/p/",
        "is_assured": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["xiaomi 14", "mi 14"],
    },
    {
        "product_id": "MOBG7BXKPNMZ9QRS",
        "name": "Redmi Note 13 Pro+ 5G (12GB RAM, 256GB) Aurora Purple",
        "brand": "Redmi",
        "model_number": "Redmi Note 13 Pro+ 256GB",
        "price": 31999.0,
        "mrp": 35999.0,
        "rating": 4.2,
        "reviews_count": 18700,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/mobile/h/k/s/-original-imagpqsbtfnhgfza.jpeg",
        "product_url": "https://www.flipkart.com/redmi-note-13-pro-plus-aurora-purple-256gb/p/",
        "is_assured": True,
        "delivery_days": 2,
        "category": "mobiles",
        "keywords": ["redmi note 13 pro plus", "redmi note 13 pro+", "redmi note 13"],
    },
    # -------- Laptops --------
    {
        "product_id": "COMGFEDSMHZFMKXF",
        "name": "Apple MacBook Air 13 inch M2 (8GB RAM, 256GB SSD) Midnight",
        "brand": "Apple",
        "model_number": "MacBook Air M2 256GB",
        "price": 96990.0,
        "mrp": 114900.0,
        "rating": 4.7,
        "reviews_count": 12400,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/computer/k/5/x/-original-imagfgwvyxqhrjnz.jpeg",
        "product_url": "https://www.flipkart.com/apple-macbook-air-m2-midnight-256gb/p/",
        "is_assured": True,
        "delivery_days": 3,
        "category": "laptops",
        "keywords": ["macbook air m2", "macbook air 13", "apple laptop m2"],
    },
    {
        "product_id": "COMGFDXTZPMKNZCD",
        "name": "Apple MacBook Pro 14 M3 Pro (18GB RAM, 512GB) Space Black",
        "brand": "Apple",
        "model_number": "MacBook Pro M3 Pro 512GB",
        "price": 204990.0,
        "mrp": 229900.0,
        "rating": 4.8,
        "reviews_count": 3100,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/computer/k/5/x/-original-imagfgwvyxqhrjnz.jpeg",
        "product_url": "https://www.flipkart.com/apple-macbook-pro-m3-pro-space-black-512gb/p/",
        "is_assured": True,
        "delivery_days": 4,
        "category": "laptops",
        "keywords": ["macbook pro m3", "macbook pro 14", "apple macbook pro"],
    },
    {
        "product_id": "COMGF7XBQNHKZPRT",
        "name": "ASUS ROG Strix G16 (Intel i9-14900HX, 16GB RAM, 1TB SSD, RTX 4070)",
        "brand": "ASUS",
        "model_number": "ROG Strix G16 2024",
        "price": 154990.0,
        "mrp": 189990.0,
        "rating": 4.4,
        "reviews_count": 2800,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/computer/y/9/e/-original-imagz5dxqjzdpghm.jpeg",
        "product_url": "https://www.flipkart.com/asus-rog-strix-g16-rtx-4070/p/",
        "is_assured": True,
        "delivery_days": 4,
        "category": "laptops",
        "keywords": ["asus rog strix g16", "rog gaming laptop", "asus rog rtx 4070"],
    },
    # -------- Audio --------
    {
        "product_id": "ACCHXMFTJXU3G2KH",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones Black",
        "brand": "Sony",
        "model_number": "WH-1000XM5",
        "price": 25990.0,
        "mrp": 34990.0,
        "rating": 4.6,
        "reviews_count": 21300,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/g/j/z/-original-imagnfhb4ey7gzgr.jpeg",
        "product_url": "https://www.flipkart.com/sony-wh-1000xm5-noise-cancelling-headphones/p/",
        "is_assured": True,
        "delivery_days": 2,
        "category": "audio",
        "keywords": ["sony wh-1000xm5", "sony headphones noise cancelling", "sony xm5"],
    },
    {
        "product_id": "ACCHZB5TQPFN3XYM",
        "name": "Apple AirPods Pro (2nd Gen) with USB-C",
        "brand": "Apple",
        "model_number": "AirPods Pro 2nd Gen",
        "price": 20900.0,
        "mrp": 24900.0,
        "rating": 4.5,
        "reviews_count": 24800,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/f/q/b/-original-imaghz3ykqhcfxzf.jpeg",
        "product_url": "https://www.flipkart.com/apple-airpods-pro-2nd-gen-usb-c/p/",
        "is_assured": True,
        "delivery_days": 2,
        "category": "audio",
        "keywords": ["airpods pro 2", "apple airpods pro", "airpods pro usb-c"],
    },
    {
        "product_id": "ACCH8YMTNPQB4XKL",
        "name": "boAt Airdopes 141 v2 Bluetooth True Wireless Earbuds",
        "brand": "boAt",
        "model_number": "Airdopes 141 v2",
        "price": 849.0,
        "mrp": 1999.0,
        "rating": 4.0,
        "reviews_count": 71600,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/headphone/t/e/c/-original-imagpz5xgbpnqgvh.jpeg",
        "product_url": "https://www.flipkart.com/boat-airdopes-141-v2/p/",
        "is_assured": True,
        "delivery_days": 3,
        "category": "audio",
        "keywords": ["boat airdopes 141", "boat earbuds", "boat airdopes"],
    },
    # -------- TVs --------
    {
        "product_id": "TVSG8X2ZQPFHM7ND",
        "name": "Samsung 55 inch 4K QLED Smart TV QN90D",
        "brand": "Samsung",
        "model_number": "QA55QN90D",
        "price": 82990.0,
        "mrp": 164900.0,
        "rating": 4.3,
        "reviews_count": 5400,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/television/m/r/8/-original-imagfzg3pnhxvjax.jpeg",
        "product_url": "https://www.flipkart.com/samsung-55-qled-4k-tv-qn90d/p/",
        "is_assured": True,
        "delivery_days": 4,
        "category": "tvs",
        "keywords": ["samsung 55 inch qled", "samsung 4k qled tv", "samsung qled 55"],
    },
    {
        "product_id": "TVSLG9ZXBNMQ8KTF",
        "name": "LG 55 inch 4K OLED evo Smart TV OLED55C3",
        "brand": "LG",
        "model_number": "OLED55C3",
        "price": 112990.0,
        "mrp": 169990.0,
        "rating": 4.6,
        "reviews_count": 3500,
        "image_url": "https://rukminim2.flixcart.com/image/612/612/xif0q/television/m/d/h/-original-imagz6g4pnqbxkfh.jpeg",
        "product_url": "https://www.flipkart.com/lg-55-oled-c3-4k-tv/p/",
        "is_assured": True,
        "delivery_days": 5,
        "category": "tvs",
        "keywords": ["lg 55 oled", "lg oled c3", "lg oled tv 55"],
    },
]


def _match_query(query: str, product: dict) -> bool:
    q = query.lower()
    name_lower = product["name"].lower()
    if q in name_lower:
        return True
    for kw in product.get("keywords", []):
        if q in kw or kw in q:
            return True
    q_words = set(q.split())
    name_words = set(name_lower.split())
    overlap = q_words & name_words
    return len(overlap) >= 1 and len(q_words) > 0


class FlipkartService:
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
        await asyncio.sleep(0.06)
        results = []
        for p in _MOCK_PRODUCTS:
            if category and p.get("category") != category:
                continue
            if not _match_query(query, p):
                continue
            import random
            price_variation = random.uniform(0.96, 1.04)
            varied_price = round(p["price"] * price_variation, -1)

            results.append(
                PlatformProduct(
                    platform=PlatformOut.FLIPKART,
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
                    is_assured=p.get("is_assured", False),
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
        raise NotImplementedError(
            "Real Flipkart API integration requires credentials. "
            "Set USE_MOCK_DATA=false and fill .env with Flipkart token."
        )
