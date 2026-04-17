"""
Product Matching Engine
-----------------------
Matches products from Amazon and Flipkart using:
  1. Exact model number match (highest confidence)
  2. Brand + partial model token overlap
  3. Title similarity via RapidFuzz (token_sort_ratio)

Returns a list of MatchedProduct objects with both platform prices.
"""
import re
import logging
from typing import List, Optional, Tuple
from rapidfuzz import fuzz
from app.schemas.product import PlatformProduct, MatchedProduct, PlatformOut

logger = logging.getLogger(__name__)

# Confidence thresholds
MODEL_EXACT_SCORE = 100
TITLE_MATCH_THRESHOLD = 72   # minimum fuzz score to consider a match


def _normalize_model(model: Optional[str]) -> str:
    """Lowercase, strip spaces and special chars from model numbers."""
    if not model:
        return ""
    return re.sub(r"[\s\-_/]", "", model.lower())


def _normalize_title(name: str) -> str:
    """Remove common noise words, lowercase."""
    noise = {
        "with", "for", "the", "a", "an", "and", "or", "in", "at", "of",
        "smartphone", "mobile", "phone", "laptop", "computer", "notebook",
        "wireless", "bluetooth", "true", "inch", "smart", "tv", "television",
    }
    tokens = re.sub(r"[^\w\s]", " ", name.lower()).split()
    return " ".join(t for t in tokens if t not in noise)


def _extract_storage_variants(name: str) -> List[str]:
    """Extract storage mentions like '128gb', '256 gb', '512gb'."""
    return re.findall(r"\d+\s*(?:gb|tb)", name.lower().replace(" ", ""))


def _models_match(a: Optional[str], b: Optional[str]) -> bool:
    na, nb = _normalize_model(a), _normalize_model(b)
    if not na or not nb:
        return False
    # Exact match
    if na == nb:
        return True
    # One contains the other (handles suffix variants)
    if na in nb or nb in na:
        return True
    return False


def _titles_match(a: str, b: str) -> Tuple[bool, float]:
    na, nb = _normalize_title(a), _normalize_title(b)

    # Check storage variants don't clash (e.g., 128GB vs 256GB)
    variants_a = _extract_storage_variants(a)
    variants_b = _extract_storage_variants(b)
    if variants_a and variants_b and not set(variants_a) & set(variants_b):
        return False, 0.0

    score = fuzz.token_sort_ratio(na, nb)
    return score >= TITLE_MATCH_THRESHOLD, score


def match_products(
    amazon_products: List[PlatformProduct],
    flipkart_products: List[PlatformProduct],
) -> List[MatchedProduct]:
    """
    Cross-match Amazon and Flipkart product lists.
    Returns merged MatchedProduct list sorted by deal_score descending.
    """
    matched: List[MatchedProduct] = []
    used_flipkart_ids = set()

    for amz in amazon_products:
        best_fk: Optional[PlatformProduct] = None
        best_score = 0.0

        for fk in flipkart_products:
            if fk.product_id in used_flipkart_ids:
                continue

            # Tier 1: model number exact match
            if _models_match(amz.model_number, fk.model_number):
                best_fk = fk
                best_score = 100.0
                break

            # Tier 2: same brand + title similarity
            if (
                amz.brand
                and fk.brand
                and amz.brand.lower() == fk.brand.lower()
            ):
                matched_flag, score = _titles_match(amz.name, fk.name)
                if matched_flag and score > best_score:
                    best_fk = fk
                    best_score = score
            else:
                # Tier 3: pure title similarity (higher threshold)
                matched_flag, score = _titles_match(amz.name, fk.name)
                if matched_flag and score >= 82 and score > best_score:
                    best_fk = fk
                    best_score = score

        merged = _build_matched(amz, best_fk)
        matched.append(merged)
        if best_fk:
            used_flipkart_ids.add(best_fk.product_id)

    # Add unmatched Flipkart products (Flipkart-only)
    for fk in flipkart_products:
        if fk.product_id not in used_flipkart_ids:
            merged = _build_matched(None, fk)
            matched.append(merged)

    # Sort by deal_score descending
    matched.sort(key=lambda x: x.deal_score, reverse=True)
    return matched


def _build_matched(
    amz: Optional[PlatformProduct],
    fk: Optional[PlatformProduct],
) -> MatchedProduct:
    """Merge a single Amazon + Flipkart pair into a MatchedProduct."""
    # Use the richer name/brand
    name = (amz or fk).name  # type: ignore[union-attr]
    brand = (amz or fk).brand  # type: ignore[union-attr]
    model_number = (amz.model_number if amz else None) or (fk.model_number if fk else None)
    category = (amz.category if amz else None) or (fk.category if fk else None)
    image_url = (amz.image_url if amz else None) or (fk.image_url if fk else None)

    # Determine best price
    prices = {}
    if amz:
        prices[PlatformOut.AMAZON] = amz.price
    if fk:
        prices[PlatformOut.FLIPKART] = fk.price

    best_platform = min(prices, key=prices.get) if prices else None
    best_price = prices[best_platform] if best_platform else None

    # Max discount
    mrp = (
        (amz.mrp if amz else None) or (fk.mrp if fk else None)
    )
    max_discount_pct: Optional[float] = None
    if mrp and best_price and mrp > 0:
        max_discount_pct = round((1 - best_price / mrp) * 100, 1)

    # Deal score (weighted)
    deal_score = _compute_deal_score(
        best_price=best_price,
        mrp=mrp,
        amazon_rating=amz.rating if amz else None,
        flipkart_rating=fk.rating if fk else None,
        discount_pct=max_discount_pct,
        amz_delivery=amz.delivery_days if amz else None,
        fk_delivery=fk.delivery_days if fk else None,
    )

    return MatchedProduct(
        name=name,
        brand=brand,
        model_number=model_number,
        category=category,
        image_url=image_url,
        # Amazon
        amazon_price=amz.price if amz else None,
        amazon_mrp=amz.mrp if amz else None,
        amazon_rating=amz.rating if amz else None,
        amazon_reviews=amz.reviews_count if amz else None,
        amazon_url=amz.product_url if amz else None,
        amazon_prime=amz.is_prime if amz else False,
        amazon_delivery_days=amz.delivery_days if amz else None,
        # Flipkart
        flipkart_price=fk.price if fk else None,
        flipkart_mrp=fk.mrp if fk else None,
        flipkart_rating=fk.rating if fk else None,
        flipkart_reviews=fk.reviews_count if fk else None,
        flipkart_url=fk.product_url if fk else None,
        flipkart_assured=fk.is_assured if fk else False,
        flipkart_delivery_days=fk.delivery_days if fk else None,
        # Derived
        best_price=best_price,
        best_platform=best_platform,
        max_discount_pct=max_discount_pct,
        deal_score=deal_score,
    )


def _compute_deal_score(
    best_price: Optional[float],
    mrp: Optional[float],
    amazon_rating: Optional[float],
    flipkart_rating: Optional[float],
    discount_pct: Optional[float],
    amz_delivery: Optional[int],
    fk_delivery: Optional[int],
) -> float:
    """
    Weighted deal score 0–100:
      Price (discount)  60%
      Rating            20%
      Discount %        10%
      Delivery speed    10%
    """
    score = 0.0

    # Price component: higher discount = higher score (max 60)
    if discount_pct is not None:
        score += min(discount_pct / 80.0, 1.0) * 60

    # Rating component (max 20)
    avg_rating = None
    ratings = [r for r in [amazon_rating, flipkart_rating] if r is not None]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        score += (avg_rating / 5.0) * 20

    # Explicit discount presence (max 10)
    if discount_pct and discount_pct > 0:
        score += min(discount_pct / 50.0, 1.0) * 10

    # Delivery speed (max 10): 1 day = 10, 5+ days = 0
    delivery = None
    deliveries = [d for d in [amz_delivery, fk_delivery] if d is not None]
    if deliveries:
        delivery = min(deliveries)
        score += max(0, (5 - delivery) / 4.0) * 10

    return round(score, 2)


def mark_best_deals(products: List[MatchedProduct]) -> List[MatchedProduct]:
    """Mark the top product in the list as 'is_best_deal'."""
    if not products:
        return products
    top_score = products[0].deal_score
    for p in products:
        p.is_best_deal = p.deal_score == top_score
    return products
