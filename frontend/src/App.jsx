import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [minRating, setMinRating] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const pageSize = 12;

  useEffect(() => {
    fetch(`${API_URL}/api/categories`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load categories");
        }
        return response.json();
      })
      .then(setCategories)
      .catch(() => setError("Unable to load categories."));
  }, []);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchProducts() {
      setLoading(true);
      setError("");

      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      });

      if (search.trim()) params.set("search", search.trim());
      if (categoryId) params.set("category_id", categoryId);
      if (minPrice !== "") params.set("min_price", minPrice);
      if (maxPrice !== "") params.set("max_price", maxPrice);
      if (minRating !== "") params.set("min_rating", minRating);

      try {
        const response = await fetch(
          `${API_URL}/api/products?${params.toString()}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Failed to load products");
        }

        const data = await response.json();
        setProducts(data.products);
        setTotal(data.total);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(
            "Unable to load products. Make sure your FastAPI backend is running."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    fetchProducts();

    return () => controller.abort();
  }, [search, categoryId, minPrice, maxPrice, minRating, page]);

  function resetFilters() {
    setSearch("");
    setCategoryId("");
    setMinPrice("");
    setMaxPrice("");
    setMinRating("");
    setPage(1);
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="app">
      <header className="navbar">
        <a className="brand" href="/">
          <span className="brand-icon">S</span>
          <span>ShopMate</span>
        </a>

        <form
          className="nav-search"
          onSubmit={(event) => {
            event.preventDefault();
            setPage(1);
          }}
        >
          <span>⌕</span>
          <input
            type="search"
            placeholder="Search for products..."
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
          />
        </form>

        <div className="nav-label">Smart Shopping</div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <span className="eyebrow">YOUR PERSONAL SHOPPING ASSISTANT</span>
            <h1>
              Find what you love.
              <br />
              <span>Shop smarter.</span>
            </h1>
            <p>
              Explore products, compare prices, and discover options that
              match your needs.
            </p>
            <a className="hero-button" href="#products">
              Explore products <span>→</span>
            </a>
          </div>

          <div className="hero-decoration" aria-hidden="true">
            <div className="hero-circle circle-one"></div>
            <div className="hero-circle circle-two"></div>
            <div className="hero-product">✦</div>
            <div className="floating-tag">Discover more</div>
          </div>
        </section>

        <section className="category-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">EXPLORE</span>
              <h2>Browse categories</h2>
            </div>
            <span className="muted">{categories.length} categories</span>
          </div>

          <div className="category-list">
            <button
              className={`category-chip ${categoryId === "" ? "active" : ""}`}
              onClick={() => {
                setCategoryId("");
                setPage(1);
              }}
            >
              All products
            </button>

            {categories.slice(0, 11).map((category) => (
              <button
                key={category.id}
                className={`category-chip ${
                  categoryId === String(category.id) ? "active" : ""
                }`}
                onClick={() => {
                  setCategoryId(String(category.id));
                  setPage(1);
                }}
                title={category.category_name}
              >
                {category.category_name}
              </button>
            ))}
          </div>
        </section>

        <section className="catalog-section" id="products">
          <div className="section-heading">
            <div>
              <span className="eyebrow">THE COLLECTION</span>
              <h2>Explore products</h2>
              <p className="muted">
                {total.toLocaleString()} matching products
              </p>
            </div>

            <button className="reset-button" onClick={resetFilters}>
              Reset filters ↺
            </button>
          </div>

          <div className="catalog-layout">
            <aside className="filters">
              <h3>Filters</h3>

              <label htmlFor="category">Category</label>
              <select
                id="category"
                value={categoryId}
                onChange={(event) => {
                  setCategoryId(event.target.value);
                  setPage(1);
                }}
              >
                <option value="">All categories</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.id}>
                    {category.category_name}
                  </option>
                ))}
              </select>

              <div className="filter-divider"></div>

              <label htmlFor="min-price">Minimum price ($)</label>
              <input
                id="min-price"
                type="number"
                min="0"
                placeholder="0"
                value={minPrice}
                onChange={(event) => {
                  setMinPrice(event.target.value);
                  setPage(1);
                }}
              />

              <label htmlFor="max-price">Maximum price ($)</label>
              <input
                id="max-price"
                type="number"
                min="0"
                placeholder="Any price"
                value={maxPrice}
                onChange={(event) => {
                  setMaxPrice(event.target.value);
                  setPage(1);
                }}
              />

              <div className="filter-divider"></div>

              <label htmlFor="rating">Minimum rating</label>
              <select
                id="rating"
                value={minRating}
                onChange={(event) => {
                  setMinRating(event.target.value);
                  setPage(1);
                }}
              >
                <option value="">Any rating</option>
                <option value="3">3+ stars</option>
                <option value="4">4+ stars</option>
                <option value="4.5">4.5+ stars</option>
              </select>

              <p className="filter-note">
                Product prices are displayed in USD from the source dataset.
              </p>
            </aside>

            <div className="products-area">
              {loading && <p className="status-message">Loading products…</p>}

              {!loading && error && (
                <div className="error-message">{error}</div>
              )}

              {!loading && !error && products.length === 0 && (
                <div className="empty-state">
                  <span>⌕</span>
                  <h3>No products found</h3>
                  <p>Try changing your search or filters.</p>
                  <button className="reset-button" onClick={resetFilters}>
                    Clear filters
                  </button>
                </div>
              )}

              {!loading && !error && products.length > 0 && (
                <>
                  <div className="products-grid">
                    {products.map((product) => (
                      <article className="product-card" key={product.asin}>
                        <div className="product-image">
                          {product.imgUrl ? (
                            <img
                              src={product.imgUrl}
                              alt={product.title}
                              loading="lazy"
                              onError={(event) => {
                                event.currentTarget.style.display = "none";
                              }}
                            />
                          ) : (
                            <span className="image-placeholder">◇</span>
                          )}

                          {product.isBestSeller && (
                            <span className="best-seller">Bestseller</span>
                          )}
                        </div>

                        <div className="product-info">
                          <p className="product-category">
                            {categories.find(
                              (category) =>
                                category.id === product.category_id
                            )?.category_name || "Product"}
                          </p>

                          <h3 title={product.title}>{product.title}</h3>

                          <div className="product-rating">
                            <span>★</span>
                            {product.stars ?? "Not rated"}
                            {product.reviews != null && (
                              <span className="review-count">
                                ({product.reviews.toLocaleString()})
                              </span>
                            )}
                          </div>

                          <div className="product-bottom">
                            <div>
                              <span className="product-price">
                                {product.price != null
                                  ? `$${product.price.toFixed(2)}`
                                  : "Price unavailable"}
                              </span>

                              {product.listPrice > 0 &&
                                product.price != null &&
                                product.listPrice > product.price && (
                                  <span className="old-price">
                                    ${product.listPrice.toFixed(2)}
                                  </span>
                                )}
                            </div>

                            {product.productURL && (
                              <a
                                className="view-product"
                                href={product.productURL}
                                target="_blank"
                                rel="noreferrer"
                              >
                                View ↗
                              </a>
                            )}
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>

                  <div className="pagination">
                    <button
                      disabled={page <= 1}
                      onClick={() => setPage((current) => current - 1)}
                    >
                      ← Previous
                    </button>

                    <span>
                      Page {page} of {Math.max(totalPages, 1)}
                    </span>

                    <button
                      disabled={page >= totalPages}
                      onClick={() => setPage((current) => current + 1)}
                    >
                      Next →
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <a className="brand" href="/">
          <span className="brand-icon">S</span>
          <span>ShopMate</span>
        </a>
        <p>Smarter shopping, built around your needs.</p>
        <span>Memory-Safe Personal Shopping Agent</span>
      </footer>
    </div>
  );
}

export default App;