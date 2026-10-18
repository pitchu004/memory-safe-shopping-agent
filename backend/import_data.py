import pandas as pd

from pathlib import Path
from sqlalchemy.dialects.sqlite import insert

from database import SessionLocal
from models import Category, Product


# --------------------------------------------------
# 1. Dataset paths
# --------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent / "data"

CATEGORIES_FILE = DATA_DIR / "amazon_categories.csv"
PRODUCTS_FILE = DATA_DIR / "amazon_products.csv"

BATCH_SIZE = 5000


# --------------------------------------------------
# 2. Helper function to clean missing values
# --------------------------------------------------

def clean_value(value):
    """Convert Pandas missing values into Python None."""

    if pd.isna(value):
        return None

    return value


# --------------------------------------------------
# 3. Import categories
# --------------------------------------------------

def import_categories(db):
    print("\nImporting categories...")

    total = 0

    for chunk in pd.read_csv(
        CATEGORIES_FILE,
        chunksize=BATCH_SIZE
    ):
        records = []

        for row in chunk.to_dict(orient="records"):
            records.append({
                "id": int(row["id"]),
                "category_name": str(row["category_name"])
            })

        if records:
            statement = insert(Category).values(records)

            statement = statement.on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "category_name": statement.excluded.category_name
                }
            )

            db.execute(statement)
            db.commit()

            total += len(records)

    print(f"Categories processed: {total}")


# --------------------------------------------------
# 4. Import products in batches
# --------------------------------------------------

def import_products(db):
    print("\nImporting products...")

    total = 0

    for chunk in pd.read_csv(
        PRODUCTS_FILE,
        chunksize=BATCH_SIZE
    ):
        records = []

        for row in chunk.to_dict(orient="records"):

            asin = clean_value(row["asin"])

            # A product must have a unique identifier.
            if asin is None or not str(asin).strip():
                continue

            records.append({
                "asin": str(asin),
                "title": (
                    str(row["title"])
                    if clean_value(row["title"]) is not None
                    else "Untitled product"
                ),
                "imgUrl": clean_value(row["imgUrl"]),
                "productURL": clean_value(row["productURL"]),
                "stars": clean_value(row["stars"]),
                "reviews": clean_value(row["reviews"]),
                "price": clean_value(row["price"]),
                "listPrice": clean_value(row["listPrice"]),
                "category_id": clean_value(row["category_id"]),
                "isBestSeller": clean_value(row["isBestSeller"]),
                "boughtInLastMonth": clean_value(
                    row["boughtInLastMonth"]
                )
            })

        if records:
            # Insert smaller batches to avoid SQLite's parameter limit.
            for start in range(0, len(records), 50):
                small_batch = records[start:start + 50]

                statement = insert(Product).values(small_batch)

                statement = statement.on_conflict_do_update(
                    index_elements=["asin"],
                    set_={
                        column: getattr(statement.excluded, column)
                        for column in [
                            "title",
                            "imgUrl",
                            "productURL",
                            "stars",
                            "reviews",
                            "price",
                            "listPrice",
                            "category_id",
                            "isBestSeller",
                            "boughtInLastMonth"
                        ]
                    }
                )

                db.execute(statement)

            db.commit()
            total += len(records)

        print(f"Products processed: {total:,}", end="\r")

    print(f"\nProducts processed: {total:,}")


# --------------------------------------------------
# 5. Main function
# --------------------------------------------------

def main():
    if not CATEGORIES_FILE.exists():
        raise FileNotFoundError(CATEGORIES_FILE)

    if not PRODUCTS_FILE.exists():
        raise FileNotFoundError(PRODUCTS_FILE)

    db = SessionLocal()

    try:
        import_categories(db)
        import_products(db)

        print("\nDataset import completed successfully!")

        print(
            "Total categories in database:",
            db.query(Category).count()
        )

        print(
            "Total products in database:",
            db.query(Product).count()
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()