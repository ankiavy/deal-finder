import logging
from typing import Optional, List
from fastapi import APIRouter, Query

from app.schemas.product import DealsResponse, DealCard, CategoryOut
from app.services.cache_service import cache_get, cache_set, make_deals_key
from app.utils.affiliate import CURATED_DEALS, build_deal_record
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory deal store for mock mode (swap for DB in production)
_DEAL_CACHE: List[dict] = [build_deal_record(d) for d in CURATED_DEALS]


@router.get("/deals", response_model=DealsResponse)
async def get_deals(
    category: Optional[CategoryOut] = Query(None, description="Filter by product category"),
    platform: Optional[str] = Query(None, description="Filter: amazon | flipkart"),
    sort_by: str = Query("discount", description="Sort by: discount | rating | newest | flash"),
    limit: int = Query(20, ge=1, le=50),
    page: int = Query(1, ge=1),
):
    """
    Returns curated deals, optionally filtered by category, platform, and sorted.
    """
    cache_key = make_deals_key(category.value if category else None, page)

    cached = await cache_get(cache_key)
    if cached:
        cached["cached"] = True
        return DealsResponse(**cached)

    try:
        deals = list(_DEAL_CACHE)

        # Filter by category
        if category:
            deals = [d for d in deals if d.get("category") == category.value]

        # Filter by platform
        if platform and platform in ("amazon", "flipkart"):
            deals = [d for d in deals if d.get("platform") == platform]

        # Sort
        if sort_by == "discount":
            deals.sort(key=lambda d: d.get("discount_pct") or 0, reverse=True)
        elif sort_by == "rating":
            deals.sort(key=lambda d: d.get("rating") or 0, reverse=True)
        elif sort_by == "flash":
            deals.sort(
                key=lambda d: (d.get("is_flash_deal", False), d.get("discount_pct") or 0),
                reverse=True,
            )
        else:
            # newest / default: priority desc
            deals.sort(key=lambda d: d.get("priority", 0), reverse=True)

        # Pagination
        offset = (page - 1) * limit
        paginated = deals[offset : offset + limit]

        deal_cards = [
            DealCard(
                id=d["id"],
                product_id=d["product_id"],
                title=d["title"],
                description=d.get("description"),
                category=CategoryOut(d["category"]) if d.get("category") else None,
                platform=d["platform"],
                deal_price=d["deal_price"],
                original_price=d.get("original_price"),
                discount_pct=d.get("discount_pct"),
                savings_amount=d.get("savings_amount"),
                affiliate_url=d["affiliate_url"],
                image_url=d.get("image_url"),
                brand=d.get("brand"),
                rating=d.get("rating"),
                reviews_count=d.get("reviews_count"),
                is_flash_deal=d.get("is_flash_deal", False),
                end_at=d.get("end_at"),
            )
            for d in paginated
        ]

        response_data = DealsResponse(
            category=category.value if category else None,
            total=len(deals),
            deals=deal_cards,
            cached=False,
        )

        await cache_set(
            cache_key,
            response_data.model_dump(),
            settings.deals_cache_ttl,
        )

        return response_data

    except Exception as e:
        logger.error(f"Deals endpoint error: {e}", exc_info=True)
        return DealsResponse(category=None, total=0, deals=[])


@router.get("/deals/flash", response_model=DealsResponse)
async def get_flash_deals():
    """Returns only active flash deals."""
    flash = [d for d in _DEAL_CACHE if d.get("is_flash_deal")]
    flash.sort(key=lambda d: d.get("priority", 0), reverse=True)

    deal_cards = [
        DealCard(
            id=d["id"],
            product_id=d["product_id"],
            title=d["title"],
            description=d.get("description"),
            platform=d["platform"],
            deal_price=d["deal_price"],
            original_price=d.get("original_price"),
            discount_pct=d.get("discount_pct"),
            savings_amount=d.get("savings_amount"),
            affiliate_url=d["affiliate_url"],
            image_url=d.get("image_url"),
            brand=d.get("brand"),
            rating=d.get("rating"),
            reviews_count=d.get("reviews_count"),
            is_flash_deal=True,
            end_at=d.get("end_at"),
        )
        for d in flash
    ]
    return DealsResponse(total=len(deal_cards), deals=deal_cards)
