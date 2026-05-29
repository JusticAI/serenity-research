CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL UNIQUE,
    created_at TEXT,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    url TEXT,
    likes INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    quotes INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ticker_mentions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    post_external_id TEXT NOT NULL,
    UNIQUE(ticker, post_external_id)
);

CREATE TABLE IF NOT EXISTS theme_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    theme TEXT NOT NULL,
    post_external_id TEXT NOT NULL,
    score REAL NOT NULL,
    UNIQUE(theme, post_external_id)
);

CREATE TABLE IF NOT EXISTS theses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_external_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    theme TEXT,
    confidence REAL DEFAULT 0.5,
    beneficiaries_json TEXT DEFAULT '[]',
    risks_json TEXT DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_external_id TEXT NOT NULL,
    prediction_text TEXT NOT NULL,
    prediction_date TEXT,
    status TEXT DEFAULT 'unreviewed',
    direction TEXT DEFAULT 'uncertain',
    condition_text TEXT,
    horizon TEXT,
    confidence REAL DEFAULT 0.45
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL
);
