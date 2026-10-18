from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models


# Create database tables if they do not exist.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Memory-Safe Personal Shopping Agent",
    description="Backend for our AI shopping assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 1. Home endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Memory-Safe Personal Shopping Agent Backend",
        "status": "running"
    }


# --------------------------------------------------
# 2. Health check
# --------------------------------------------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "shopping-agent-backend"
    }


# --------------------------------------------------
# 3. Get products with search and filters
# --------------------------------------------------

@app.get("/api/products")
def get_products(
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    min_rating: float | None = Query(default=None, ge=0, le=5),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product)

    # Search product titles.
    if search and search.strip():
        query = query.filter(
            models.Product.title.ilike(f"%{search.strip()}%")
        )

    # Filter by category.
    if category_id is not None:
        query = query.filter(
            models.Product.category_id == category_id
        )

    # Filter by minimum price.
    if min_price is not None:
        query = query.filter(
            models.Product.price >= min_price
        )

    # Filter by maximum price.
    if max_price is not None:
        query = query.filter(
            models.Product.price <= max_price
        )

    # Filter by minimum rating.
    if min_rating is not None:
        query = query.filter(
            models.Product.stars >= min_rating
        )

    # Count the matching records.
    total = query.count()

    # Retrieve only the requested page.
    products = (
        query
        .order_by(models.Product.asin)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "products": [
            {
                "asin": product.asin,
                "title": product.title,
                "imgUrl": product.imgUrl,
                "productURL": product.productURL,
                "stars": product.stars,
                "reviews": product.reviews,
                "price": product.price,
                "listPrice": product.listPrice,
                "category_id": product.category_id,
                "isBestSeller": product.isBestSeller,
                "boughtInLastMonth": product.boughtInLastMonth
            }
            for product in products
        ]
    }


# --------------------------------------------------
# 4. Get a specific product
# --------------------------------------------------

@app.get("/api/products/{asin}")
def get_product(
    asin: str,
    db: Session = Depends(get_db)
):
    product = (
        db.query(models.Product)
        .filter(models.Product.asin == asin)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "asin": product.asin,
        "title": product.title,
        "imgUrl": product.imgUrl,
        "productURL": product.productURL,
        "stars": product.stars,
        "reviews": product.reviews,
        "price": product.price,
        "listPrice": product.listPrice,
        "category_id": product.category_id,
        "isBestSeller": product.isBestSeller,
        "boughtInLastMonth": product.boughtInLastMonth
    }


# --------------------------------------------------
# 5. Get categories
# --------------------------------------------------

@app.get("/api/categories")
def get_categories(
    db: Session = Depends(get_db)
):
    categories = (
        db.query(models.Category)
        .order_by(models.Category.category_name)
        .all()
    )

    return [
        {
            "id": category.id,
            "category_name": category.category_name
        }
        for category in categories
    ]