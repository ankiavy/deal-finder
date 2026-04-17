import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException

from app.schemas.product import SearchResponse, CategoryOut
from app.services.amazon_service import AmazonService
from app.services.flipkart_service import FlipkartService
from app.services.matching_service import match_products, mark_best_deals
from app.services.cache_service import cache_get, cache_set, make_search_key
from app.utils.affiliate import generate_amazon_affiliate_url, generate_flipkart_affiliate_url
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

amazon_svc = AmazonService()
flipkart_svc = FlipkartService()


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=2, max_length=200, description="Product search query"),
    category: Optional[CategoryOut] = Query(None, description="Filter by category"),
    limit: int = Query(5, ge=1, le=10),
):
    """
    Search for products across Amazon and Flipkart.
    Returns top results with price comparison.
    """
    q = q.strip()
    cache_key = make_search_key(q, category.value if category else None)

    # Try cache first
    cached = await cache_get(cache_key)
    if cached:
        cached["cached"] = True
        return SearchResponse(**cached)

    try:
        # Fetch from both platforms concurrently
        amazon_task = asyncio.create_task(
            amazon_svc.search(q, category.value if category else None, limit=10)
        )
        flipkart_task = asyncio.create_task(
            flipkart_svc.search(q, category.value if category else None, limit=10)
        )

        amazon_results, flipkart_results = await asyncio.gather(
            amazon_task, flipkart_task, return_exceptions=True
        )

        # Handle partial failures gracefully
        if isinstance(amazon_results, Exception):
            logger.warning(f"Amazon search failed: {amazon_results}")
            amazon_results = []
        if isinstance(flipkart_results, Exception):
            logger.warning(f"Flipkart search failed: {flipkart_results}")
            flipkart_results = []

        if not amazon_results and not flipkart_results:
            return SearchResponse(query=q, total=0, results=[])

        # Match products across platforms
        matched = match_products(amazon_results, flipkart_results)

        # Inject affiliate links
        for product in matched:
            if product.amazon_url:
                asin = product.amazon_url.split("/dp/")[-1].split("?")[0] if "/dp/" in product.amazon_url else ""
                if asin:
                    product.amazon_affiliate_url = generate_amazon_affiliate_url(asin)
            if product.flipkart_url:
                product.flipkart_affiliate_url = generate_flipkart_affiliate_url(product.flipkart_url)

        # Mark best deals and trim to limit
        matched = mark_best_deals(matched)
        matched = matched[:limit]

        response_data = SearchResponse(
            query=q,
            total=len(matched),
            results=matched,
            cached=False,
        )

        # Cache the result
        await cache_set(
            cache_key,
            response_data.model_dump(),
            settings.search_cache_ttl,
        )

        return response_data

    except Exception as e:
        logger.error(f"Search error for query '{q}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search service temporarily unavailable")
