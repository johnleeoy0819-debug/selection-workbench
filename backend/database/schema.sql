-- Maple Hollow Home 数据库 Schema
-- SQLite

-- 关键词表
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,
    avg_searches INTEGER,
    avg_clicks INTEGER,
    ctr INTEGER,
    competition INTEGER,
    kd INTEGER,
    tag_occurrences INTEGER DEFAULT 0,
    char_count INTEGER DEFAULT 0,
    google_searches INTEGER DEFAULT 0,
    peak_months TEXT,
    time_status TEXT CHECK(time_status IN ('urgent', 'prepare', 'plan', 'early', 'evergreen')),
    gift_potential TEXT CHECK(gift_potential IN ('high', 'medium', 'low')),
    is_selected BOOLEAN DEFAULT 0,
    source TEXT DEFAULT 'erank',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 竞品 Listing 表
CREATE TABLE IF NOT EXISTS competitor_listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_id INTEGER REFERENCES keywords(id),
    title TEXT NOT NULL,
    age_days INTEGER,
    views INTEGER,
    daily_views INTEGER,
    est_sales INTEGER,
    price REAL,
    est_revenue REAL,
    hearts INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品表
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT UNIQUE,
    name TEXT NOT NULL,
    keyword_id INTEGER REFERENCES keywords(id),
    subcategory TEXT CHECK(subcategory IN ('hook', 'desk_decor', 'wall_decor')),
    market_scope TEXT CHECK(market_scope IN ('us', 'uk', 'ca', 'us_uk_ca')),
    status TEXT DEFAULT 'pending_analysis' CHECK(status IN (
        'pending_analysis', 'analyzing', 'pending_decision', 
        'confirmed', 'listed', 'observing', 'abandoned', 'archived'
    )),
    source_type TEXT CHECK(source_type IN ('manual', 'erank', 'ai_recommend')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 产品形态表
CREATE TABLE IF NOT EXISTS product_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    material TEXT,
    dimensions TEXT,
    weight_g INTEGER,
    customization_type TEXT,
    customization_complexity TEXT CHECK(customization_complexity IN ('low', 'medium', 'high')),
    production_leadtime_days INTEGER
);

-- 供应链表
CREATE TABLE IF NOT EXISTS supply_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    supplier_source TEXT CHECK(supplier_source IN ('1688', 'taobao', 'local', 'other')),
    supplier_url TEXT,
    moq INTEGER,
    unit_cost_cny REAL,
    shipping_cost_cny REAL,
    custom_cost_cny REAL DEFAULT 0,
    packaging_cost_usd REAL DEFAULT 0.8
);

-- 定价表
CREATE TABLE IF NOT EXISTS pricings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    listing_price_usd REAL,
    total_cog_usd REAL,
    platform_fees_usd REAL,
    net_profit_usd REAL,
    net_margin_pct REAL
);

-- 市场数据表
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    data_collected_date DATE,
    etsy_search_results_count INTEGER,
    avg_price_top10_usd REAL,
    avg_reviews_top10 INTEGER,
    top10_seller_locations TEXT
);

-- 评分明细表
CREATE TABLE IF NOT EXISTS product_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    demand_score INTEGER CHECK(demand_score BETWEEN 1 AND 10),
    profit_score INTEGER CHECK(profit_score BETWEEN 1 AND 10),
    competition_score INTEGER CHECK(competition_score BETWEEN 1 AND 10),
    seasonal_score INTEGER CHECK(seasonal_score BETWEEN 1 AND 10),
    compliance_score INTEGER CHECK(compliance_score BETWEEN 1 AND 10),
    composite_score INTEGER CHECK(composite_score BETWEEN 0 AND 100),
    final_decision TEXT CHECK(final_decision IN ('execute', 'observe', 'abandon')),
    confidence_level TEXT CHECK(confidence_level IN ('high', 'medium', 'low')),
    scoring_version TEXT DEFAULT 'v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1688 采集数据表
CREATE TABLE IF NOT EXISTS source_1688 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER REFERENCES products(id),
    original_id TEXT,
    title TEXT,
    price_cny REAL,
    moq INTEGER,
    supplier TEXT,
    images TEXT,  -- JSON 数组
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS config (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    exchange_rate REAL DEFAULT 7.0,
    exchange_rate_last_updated TIMESTAMP,
    offsite_ads_threshold REAL DEFAULT 10000,
    annual_revenue REAL DEFAULT 0,
    scoring_version TEXT DEFAULT 'v1.0'
);

-- 评分权重表
CREATE TABLE IF NOT EXISTS scoring_weights (
    version TEXT PRIMARY KEY,
    demand_weight REAL DEFAULT 0.35,
    profit_weight REAL DEFAULT 0.30,
    competition_weight REAL DEFAULT 0.25,
    seasonal_weight REAL DEFAULT 0.10,
    is_active BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT OR IGNORE INTO config (id) VALUES (1);

-- 插入默认评分权重
INSERT OR IGNORE INTO scoring_weights (version, demand_weight, profit_weight, competition_weight, seasonal_weight, is_active)
VALUES ('v1.0', 0.35, 0.30, 0.25, 0.10, 1);
