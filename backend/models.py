from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    ForeignKey
)

from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(255), nullable=False)


class Product(Base):
    __tablename__ = "products"

    # Amazon product identifier
    asin = Column(String(20), primary_key=True, index=True)

    # Product information
    title = Column(Text, nullable=False)
    imgUrl = Column(Text, nullable=True)
    productURL = Column(Text, nullable=True)

    # Ratings and prices
    stars = Column(Float, nullable=True)
    reviews = Column(Integer, nullable=True)
    price = Column(Float, nullable=True)
    listPrice = Column(Float, nullable=True)

    # Category relationship
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
        index=True
    )

    # Popularity information
    isBestSeller = Column(Boolean, nullable=True)
    boughtInLastMonth = Column(Integer, nullable=True)