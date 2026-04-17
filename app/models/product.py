from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    Index,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class PlatformEnum(str, enum.Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    BOTH = "both"


class CategoryEnum(str, enum.Enum):
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


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False, index=True)
    brand = Column(String(100))
    model_number = Column(String(200), index=True)
    category = Column(Enum(CategoryEnum), default=CategoryEnum.OTHER)
    image_url = Column(Text)
    description = Column(Text)

    # Amazon data
    amazon_asin = Column(String(20), unique=True, index=True, nullable=True)
    amazon_price = Column(Float, nullable=True)
    amazon_mrp = Column(Float, nullable=True)
    amazon_rating = Column(Float, nullable=True)
    amazon_reviews = Column(Integer, nullable=True)
    amazon_url = Column(Text, nullable=True)
    amazon_prime = Column(Boolean, default=False)
    amazon_delivery_days = Column(Integer, nullable=True)

    # Flipkart data
    flipkart_id = Column(String(100), unique=True, index=True, nullable=True)
    flipkart_price = Column(Float, nullable=True)
    flipkart_mrp = Column(Float, nullable=True)
    flipkart_rating = Column(Float, nullable=True)
    flipkart_reviews = Column(Integer, nullable=True)
    flipkart_url = Column(Text, nullable=True)
    flipkart_assured = Column(Boolean, default=False)
    flipkart_delivery_days = Column(Integer, nullable=True)

    # Computed fields
    best_price = Column(Float, nullable=True)
    best_platform = Column(Enum(PlatformEnum), nullable=True)
    max_discount_pct = Column(Float, nullable=True)
    deal_score = Column(Float, default=0.0)

    # Metadata
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_products_category_score", "category", "deal_score"),
        Index("ix_products_featured", "is_featured", "deal_score"),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "brand": self.brand,
            "model_number": self.model_number,
            "category": self.category.value if self.category else None,
            "image_url": self.image_url,
            "amazon_asin": self.amazon_asin,
            "amazon_price": self.amazon_price,
            "amazon_mrp": self.amazon_mrp,
            "amazon_rating": self.amazon_rating,
            "amazon_reviews": self.amazon_reviews,
            "amazon_url": self.amazon_url,
            "amazon_prime": self.amazon_prime,
            "amazon_delivery_days": self.amazon_delivery_days,
            "flipkart_id": self.flipkart_id,
            "flipkart_price": self.flipkart_price,
            "flipkart_mrp": self.flipkart_mrp,
            "flipkart_rating": self.flipkart_rating,
            "flipkart_reviews": self.flipkart_reviews,
            "flipkart_url": self.flipkart_url,
            "flipkart_assured": self.flipkart_assured,
            "flipkart_delivery_days": self.flipkart_delivery_days,
            "best_price": self.best_price,
            "best_platform": self.best_platform.value if self.best_platform else None,
            "max_discount_pct": self.max_discount_pct,
            "deal_score": self.deal_score,
            "is_featured": self.is_featured,
        }


class Deal(Base):
    __tablename__ = "deals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(Enum(CategoryEnum), default=CategoryEnum.OTHER, index=True)
    platform = Column(Enum(PlatformEnum), nullable=False)

    # Pricing
    deal_price = Column(Float, nullable=False)
    original_price = Column(Float)
    discount_pct = Column(Float)
    savings_amount = Column(Float)

    # Affiliate URL (generated)
    affiliate_url = Column(Text, nullable=False)
    image_url = Column(Text)
    brand = Column(String(100))
    rating = Column(Float)
    reviews_count = Column(Integer)

    # Deal metadata
    is_active = Column(Boolean, default=True)
    is_flash_deal = Column(Boolean, default=False)
    priority = Column(Integer, default=0)  # manual boost
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)

    # Time bounds
    start_at = Column(DateTime(timezone=True), server_default=func.now())
    end_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("ix_deals_active_category", "is_active", "category"),
        Index("ix_deals_active_discount", "is_active", "discount_pct"),
        Index("ix_deals_flash", "is_flash_deal", "end_at"),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "product_id": str(self.product_id),
            "title": self.title,
            "description": self.description,
            "category": self.category.value if self.category else None,
            "platform": self.platform.value if self.platform else None,
            "deal_price": self.deal_price,
            "original_price": self.original_price,
            "discount_pct": self.discount_pct,
            "savings_amount": self.savings_amount,
            "affiliate_url": self.affiliate_url,
            "image_url": self.image_url,
            "brand": self.brand,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "is_flash_deal": self.is_flash_deal,
            "clicks": self.clicks,
            "end_at": self.end_at.isoformat() if self.end_at else None,
        }


class ClickTrack(Base):
    __tablename__ = "click_tracks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id = Column(
        UUID(as_uuid=True), ForeignKey("deals.id"), nullable=True, index=True
    )
    product_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    platform = Column(Enum(PlatformEnum), nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_hash = Column(String(64), nullable=True)  # hashed for privacy
    referer = Column(String(500), nullable=True)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now())
