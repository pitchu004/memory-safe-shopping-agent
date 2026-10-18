import pandas as pd
from pathlib import Path

# Locate the dataset directory
DATA_DIR = Path(__file__).resolve().parent / "data"

products_file = DATA_DIR / "amazon_products.csv"
categories_file = DATA_DIR / "amazon_categories.csv"

# Verify that both files exist
print("Products file exists:", products_file.exists())
print("Categories file exists:", categories_file.exists())

if not products_file.exists() or not categories_file.exists():
    raise FileNotFoundError(
        "Dataset files not found. Check the data folder and filenames."
    )

# Read only five rows for initial inspection
products = pd.read_csv(products_file, nrows=5)
categories = pd.read_csv(categories_file, nrows=5)

print("\n========== PRODUCTS ==========")
print("Columns:", products.columns.tolist())
print("\nSample records:")
print(products.to_string(index=False))

print("\n========== CATEGORIES ==========")
print("Columns:", categories.columns.tolist())
print("\nSample records:")
print(categories.to_string(index=False))