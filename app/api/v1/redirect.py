import hashlib
import logging
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from app.utils.affiliate import (
    CURATED_DEALS,
    build_deal_record,
    generate_amazon_affiliate_url,
    generate_flipkart_affiliate_url,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Build a lookup: deal_id -> affiliate_url
_REDIRECT_MAP: dict = {}
for _d in CURATED_DEALS:
    _rec = build_deal_record(_d)
    _REDIRECT_MAP[_rec["id"]] = _rec["affiliate_url"]


@router.get("/redirect/{token}")
async def affiliate_redirect(token: str, request: Request):
    """
    Track a click and redirect to the affiliate URL.
    token can be a deal_id UUID or a raw product ASIN/ID.
    """
    # 1. Look up in known deals
    affiliate_url = _REDIRECT_MAP.get(token)

    # 2. Fallback: if token looks like an Amazon ASIN, build link directly
    if not affiliate_url and len(token) == 10 and token.isalnum():
        affiliate_url = generate_amazon_affiliate_url(token)

    # 3. Fallback: return homepage
    if not affiliate_url:
        logger.warning(f"Unknown redirect token: {token}")
        return RedirectResponse(url="https://www.amazon.in", status_code=302)

    # Track click (log only; production would write to DB)
    try:
        user_agent = request.headers.get("user-agent", "")
        client_ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
        logger.info(
            f"CLICK token={token} ua_snippet={user_agent[:60]} ip_hash={ip_hash}"
        )
    except Exception as e:
        logger.warning(f"Click tracking error: {e}")

    return RedirectResponse(url=affiliate_url, status_code=302)
