from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional, List
from enum import Enum
import uuid


class PlatformOut(str, Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    BOTH = "both"


class CategoryOut(str, Enum):
    MOBILES = "mobiles"
    ELECTRONICS = "electronics"
    LAPTOPS = "laptops"
    AUDIO = "audio"
    TVS = "tvs"
    CAMERAS = "cameras"
    FASHION = "fashion"
    HOME = "home"
    APPLIANCES = "appliances"
    OTHER = "other"


# -----------------------------------------------------------------
# Raw product from a single platform
# -----------------------------------------------------------------
class PlatformProduct(BaseModel):
    platform: PlatformOut
    product_id: str          # ASIN or Flipkart item ID
    name: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    image_url: Optional[str] = None
    product_url: str
    is_prime: bool = False
    is_assured: bool = False
    delivery_days: Optional[int] = None
    category: Optional[CategoryOut] = None


# -----------------------------------------------------------------
# Matched product (cross-platform comparison)
# -----------------------------------------------------------------
class MatchedProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: Optional[str] = None
    model_number: Optional[str] = None
    category: Optional[CategoryOut] = None
    image_url: Optional[str] = None

    # Amazon
    amazon_price: Optional[float] = None
    amazon_mrp: Optional[float] = None
    amazon_rating: Optional[float] = None
    amazon_reviews: Optional[int] = None
    amazon_url: Optional[str] = None
    amazon_prime: bool = False
    amazon_delivery_days: Optional[int] = None

    # Flipkart
    flipkart_price: Optional[float] = None
    flipkart_mrp: Optional[float] = None
    flipkart_rating: Optional[float] = None
    flipkart_reviews: Optional[int] = None
    flipkart_url: Optional[str] = None
    flipkart_assured: bool = False
    flipkart_delivery_days: Optional[int] = None

    # Derived
    best_price: Optional[float] = None
    best_platform: Optional[PlatformOut] = None
    max_discount_pct: Optional[float] = None
    deal_score: float = 0.0
    is_best_deal: bool = False

    # Affiliate links (generated)
    amazon_affiliate_url: Optional[str] = None
    flipkart_affiliate_url: Optional[str] = None


# -----------------------------------------------------------------
# Search
# -----------------------------------------------------------------
class SearchRequest(BaseModel):
    q: str = Field(..., min_length=2, max_length=200)
    category: Optional[CategoryOut] = None
    limit: int = Field(default=5, ge=1, le=20)


class SearchResponse(BaseModel):
    query: str
    total: int
    results: List[MatchedProduct]
    cached: bool = False


# -----------------------------------------------------------------
# Deals
# -----------------------------------------------------------------
class DealCard(BaseModel):
    id: str
    product_id: str
    title: str
    description: Optional[str] = None
    category: Optional[CategoryOut] = None
    platform: PlatformOut
    deal_price: float
    original_price: Optional[float] = None
    discount_pct: Optional[float] = None
    savings_amount: Optional[float] = None
    affiliate_url: str
    image_url: Optional[str] = None
    brand: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    is_flash_deal: bool = False
    end_at: Optional[str] = None
    clicks: int = 0


class DealsResponse(BaseModel):
    category: Optional[str] = None
    total: int
    deals: List[DealCard]
    cached: bool = False


# -----------------------------------------------------------------
# Redirect
# -----------------------------------------------------------------
class RedirectResponse(BaseModel):
    redirect_url: str
    platform: PlatformOut
    tracked: bool = True
