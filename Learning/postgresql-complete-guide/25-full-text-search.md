# Full-Text Search

## Overview

PostgreSQL provides robust full-text search (FTS) capabilities built directly into the database, offering linguistic features, ranking, highlighting, and advanced query capabilities without requiring external search engines.

## Table of Contents
- [Introduction to Full-Text Search](#introduction-to-full-text-search)
- [Text Search Data Types](#text-search-data-types)
- [Text Search Functions](#text-search-functions)
- [Creating Search Documents](#creating-search-documents)
- [Search Queries](#search-queries)
- [Ranking Results](#ranking-results)
- [Text Search Indexes](#text-search-indexes)
- [Advanced Search Features](#advanced-search-features)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Introduction to Full-Text Search

### Why Full-Text Search?

```sql
-- Problem with LIKE searches:
SELECT * FROM articles 
WHERE content LIKE '%database%';
-- Issues:
-- 1. No ranking (all matches equal)
-- 2. No linguistic analysis (database vs databases)
-- 3. Cannot use indexes efficiently
-- 4. No phrase search or complex queries
-- 5. Slow on large datasets

-- Full-Text Search solution:
SELECT * FROM articles 
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'database');
-- Advantages:
-- 1. Linguistic stemming (database = databases = database's)
-- 2. Ranking by relevance
-- 3. GIN/GiST index support
-- 4. Phrase searches, proximity, boolean operators
-- 5. Fast on large datasets
```

### FTS Components

```sql
-- Full-Text Search involves:
-- 1. Documents: Text to be searched
-- 2. Tokens: Words extracted from documents
-- 3. Lexemes: Normalized tokens (stemmed)
-- 4. tsvector: Processed document representation
-- 5. tsquery: Search query representation
-- 6. Text search configuration: Language-specific rules

-- Example flow:
-- Document: "The quick brown foxes jumped"
-- Tokens: ["The", "quick", "brown", "foxes", "jumped"]
-- Lexemes: ["quick", "brown", "fox", "jump"]  -- stemmed, stop words removed
-- tsvector: 'brown':3 'fox':4 'jump':5 'quick':2
```

## Text Search Data Types

### tsvector Type

Represents processed document:

```sql
-- Create tsvector from text
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- Result: 'brown':3 'dog':9 'fox':4 'jump':5 'lazi':8 'quick':2

-- Positions indicate word locations
-- Stop words ('the', 'over') removed
-- Words stemmed ('jumps' → 'jump', 'lazy' → 'lazi')

-- Concatenate tsvectors
SELECT 
    to_tsvector('english', 'PostgreSQL Database') ||
    to_tsvector('english', 'Full Text Search');
-- Result: 'databas':2 'full':3 'postgresql':1 'search':5 'text':4

-- Direct tsvector creation (no processing)
SELECT 'fat:1 cat:2 rat:3'::tsvector;
-- Useful for pre-processed text

-- tsvector with weights (A, B, C, D for importance)
SELECT setweight(to_tsvector('english', 'PostgreSQL'), 'A') ||
       setweight(to_tsvector('english', 'Full-text search'), 'B');
-- Result: 'full':2B 'full-text':2B 'postgresql':1A 'search':4B 'text':3B

-- Extract lexemes
SELECT unnest(to_tsvector('english', 'running runners run ran'));
-- Result: 'ran', 'run', 'runner'
```

### tsquery Type

Represents search query:

```sql
-- Simple word search
SELECT to_tsquery('english', 'database');
-- Result: 'databas'

-- AND operator (&)
SELECT to_tsquery('english', 'postgresql & database');
-- Result: 'postgresql' & 'databas'

-- OR operator (|)
SELECT to_tsquery('english', 'postgresql | mysql');
-- Result: 'postgresql' | 'mysql'

-- NOT operator (!)
SELECT to_tsquery('english', 'database & !mysql');
-- Result: 'databas' & !'mysql'

-- Phrase search (<->)
SELECT to_tsquery('english', 'full <-> text <-> search');
-- Result: 'full' <-> 'text' <-> 'search'
-- Matches words in exact sequence

-- Proximity search (<N>)
SELECT to_tsquery('english', 'postgresql <2> database');
-- Matches 'postgresql' within 2 words of 'database'

-- Grouping with parentheses
SELECT to_tsquery('english', '(postgresql | mysql) & database');
-- Result: ( 'postgresql' | 'mysql' ) & 'databas'

-- plainto_tsquery: Simple query (words to AND)
SELECT plainto_tsquery('english', 'postgresql full text search');
-- Result: 'postgresql' & 'full' & 'text' & 'search'

-- phraseto_tsquery: Phrase search
SELECT phraseto_tsquery('english', 'full text search');
-- Result: 'full' <-> 'text' <-> 'search'

-- websearch_to_tsquery: Google-like syntax (PG 11+)
SELECT websearch_to_tsquery('english', 'postgresql "full text" -mysql');
-- Result: 'postgresql' & 'full' <-> 'text' & !'mysql'
-- Supports: "phrase" (quotes), -exclude (minus), OR
```

## Text Search Functions

### Basic Functions

```sql
-- to_tsvector: Convert text to tsvector
SELECT to_tsvector('english', 'PostgreSQL is a powerful database');

-- to_tsquery: Convert text to tsquery
SELECT to_tsquery('english', 'postgresql & database');

-- Match operator (@@)
SELECT 
    to_tsvector('english', 'PostgreSQL database') @@ 
    to_tsquery('english', 'postgresql');
-- Returns: true

-- Example table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO articles (title, content) VALUES
    ('Introduction to PostgreSQL', 'PostgreSQL is a powerful open-source database system.'),
    ('Full-Text Search', 'Full-text search allows finding documents by content.'),
    ('Database Indexing', 'Indexes improve query performance in databases.');

-- Search articles
SELECT title, content
FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@ 
      to_tsquery('english', 'postgresql | database');
```

### Text Search Configuration

```sql
-- List available configurations
SELECT cfgname FROM pg_ts_config;
-- Common: simple, english, spanish, french, german, etc.

-- Default configuration
SHOW default_text_search_config;
-- Usually: pg_catalog.english

-- Set default configuration
SET default_text_search_config = 'pg_catalog.english';

-- Use specific configuration
SELECT to_tsvector('spanish', 'Los rápidos zorros marrones');

-- Configuration components:
-- 1. Parser: Tokenizes text
-- 2. Dictionary: Stems and filters tokens

-- View configuration details
SELECT * FROM pg_ts_config_map WHERE mapcfgname = 'english';
```

## Creating Search Documents

### Generated Columns

```sql
-- Add tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Populate search vector
UPDATE articles 
SET search_vector = 
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- Keep updated with trigger
CREATE FUNCTION articles_search_trigger() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        to_tsvector('english', coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW
EXECUTE FUNCTION articles_search_trigger();

-- Test trigger
INSERT INTO articles (title, content) 
VALUES ('New Article', 'This is new content');

SELECT title, search_vector FROM articles WHERE title = 'New Article';
```

### Weighted Search Vectors

```sql
-- Weight different fields differently
ALTER TABLE articles ADD COLUMN weighted_search tsvector;

UPDATE articles 
SET weighted_search = 
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B');

-- A = highest importance
-- B = high importance
-- C = low importance
-- D = lowest importance

-- Trigger with weights
CREATE OR REPLACE FUNCTION articles_weighted_search_trigger() 
RETURNS trigger AS $$
BEGIN
    NEW.weighted_search := 
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER weighted_tsvector_update BEFORE INSERT OR UPDATE
ON articles FOR EACH ROW
EXECUTE FUNCTION articles_weighted_search_trigger();
```

### Generated Stored Columns (PG 12+)

```sql
-- Automatically maintained search vector
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    body TEXT,
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body, ''))
    ) STORED
);

-- Automatically updated on INSERT/UPDATE
INSERT INTO blog_posts (title, body) 
VALUES ('PostgreSQL 14', 'New features in PostgreSQL 14');

SELECT title, search_vector FROM blog_posts;
```

## Search Queries

### Basic Searches

```sql
-- Simple word search
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'database');

-- Multiple words (AND)
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql & database');

-- Multiple words (OR)
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql | mysql');

-- Exclude words (NOT)
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'database & !mysql');

-- Using plainto_tsquery (easier)
SELECT title, content
FROM articles
WHERE search_vector @@ plainto_tsquery('english', 'postgresql database');
-- Automatically adds & between words
```

### Phrase Searches

```sql
-- Exact phrase
SELECT title, content
FROM articles
WHERE search_vector @@ phraseto_tsquery('english', 'full text search');

-- Phrase with proximity
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'full <-> text <-> search');

-- Words within N positions
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql <3> database');
-- Matches if 'postgresql' within 3 words of 'database'
```

### Complex Queries

```sql
-- Boolean combinations
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 
    '(postgresql | mysql) & (database | rdbms) & !oracle'
);

-- Prefix matching (for autocomplete)
SELECT title, content
FROM articles
WHERE search_vector @@ to_tsquery('english', 'data:*');
-- Matches: database, data, datasets, etc.

-- Web-style search (PG 11+)
SELECT title, content
FROM articles
WHERE search_vector @@ websearch_to_tsquery('english', 
    'postgresql "full text" -oracle OR mysql'
);
-- Supports Google-like syntax
```

## Ranking Results

### Basic Ranking

```sql
-- ts_rank: Basic relevance ranking
SELECT 
    title,
    ts_rank(search_vector, query) as rank
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query
ORDER BY rank DESC;

-- ts_rank considers:
-- 1. Number of matches
-- 2. Proximity of matches
-- 3. Word positions

-- ts_rank_cd: Cover density ranking (better for long documents)
SELECT 
    title,
    ts_rank_cd(search_vector, query) as rank
FROM articles, to_tsquery('english', 'postgresql & database') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Weighted Ranking

```sql
-- Use weights in ranking
SELECT 
    title,
    ts_rank(weighted_search, query) as rank
FROM articles, to_tsquery('english', 'database') query
WHERE weighted_search @@ query
ORDER BY rank DESC;

-- Custom weight values
SELECT 
    title,
    ts_rank(
        weighted_search, 
        query,
        1 | 2  -- normalization flags
    ) as rank
FROM articles, to_tsquery('english', 'database') query
WHERE weighted_search @@ query
ORDER BY rank DESC;

-- Normalization flags:
-- 0: No normalization (default)
-- 1: Divide by 1 + log(document length)
-- 2: Divide by document length
-- 4: Divide by mean harmonic distance
-- 8: Divide by unique words
-- 16: Divide by 1 + log(unique words)
-- 32: Divide by rank itself
```

### Custom Ranking

```sql
-- Combine multiple factors
SELECT 
    title,
    content,
    ts_rank(search_vector, query) as text_rank,
    log(views + 1) as popularity,
    extract(epoch from (now() - created_at))/86400 as days_old,
    -- Custom score
    ts_rank(search_vector, query) * 
    log(views + 1) * 
    (1.0 / (1 + extract(epoch from (now() - created_at))/86400/365)) as custom_score
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query
ORDER BY custom_score DESC;
```

## Text Search Indexes

### GIN Indexes

Most common for full-text search:

```sql
-- Create GIN index
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- Query uses index automatically
EXPLAIN ANALYZE
SELECT title FROM articles
WHERE search_vector @@ to_tsquery('english', 'database');
-- Shows: Bitmap Index Scan using idx_articles_search

-- GIN index on expression
CREATE INDEX idx_articles_title_content 
ON articles USING GIN(to_tsvector('english', title || ' ' || content));

-- Multi-column GIN index
CREATE INDEX idx_articles_multi 
ON articles USING GIN((
    setweight(to_tsvector('english', title), 'A') ||
    setweight(to_tsvector('english', content), 'B')
));
```

### GiST Indexes

Better for frequent updates:

```sql
-- Create GiST index
CREATE INDEX idx_articles_search_gist ON articles USING GIST(search_vector);

-- GIN vs GiST comparison:
-- GIN:
--   + Faster searches (3x faster)
--   + Smaller index size
--   - Slower updates
--   - Larger build time
-- GiST:
--   + Faster updates
--   + Faster build
--   - Slower searches
--   - Larger index size

-- Use GIN for mostly-read data
-- Use GiST for frequently-updated data
```

### Partial Indexes

```sql
-- Index only recent articles
CREATE INDEX idx_recent_articles_search 
ON articles USING GIN(search_vector)
WHERE created_at > now() - interval '1 year';

-- Index only published articles
CREATE INDEX idx_published_search 
ON articles USING GIN(search_vector)
WHERE status = 'published';
```

## Advanced Search Features

### Highlighting Matches

```sql
-- ts_headline: Highlight search matches
SELECT 
    title,
    ts_headline('english', content, query) as highlighted
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query;

-- Output example:
-- "PostgreSQL is a powerful <b>database</b> system."

-- Custom highlighting options
SELECT 
    title,
    ts_headline('english', content, query,
        'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=25'
    ) as highlighted
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query;

-- Options:
-- StartSel: Opening tag (default: <b>)
-- StopSel: Closing tag (default: </b>)
-- MaxWords: Maximum words in headline
-- MinWords: Minimum words in headline
-- ShortWord: Words <= this ignored (default: 3)
-- HighlightAll: Highlight all matches (default: false)
-- MaxFragments: Number of fragments (default: 0)
-- FragmentDelimiter: Between fragments (default: ' ... ')
```

### Autocomplete/Suggest

```sql
-- Prefix matching for autocomplete
SELECT DISTINCT 
    word
FROM ts_stat('SELECT search_vector FROM articles')
WHERE word LIKE 'data%'
ORDER BY word
LIMIT 10;

-- Build autocomplete suggestions table
CREATE TABLE search_suggestions (
    term TEXT PRIMARY KEY,
    frequency INTEGER,
    search_vector tsvector
);

-- Populate from search queries
INSERT INTO search_suggestions (term, frequency)
SELECT query, count(*) 
FROM search_logs
GROUP BY query;

-- Fuzzy matching with trigrams
CREATE EXTENSION pg_trgm;

SELECT term
FROM search_suggestions
WHERE term % 'databas'  -- Similar to
ORDER BY similarity(term, 'databas') DESC
LIMIT 10;
```

### Multi-language Search

```sql
-- Detect language and search
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    language TEXT,
    search_vector tsvector
);

-- Populate with language-specific vectors
INSERT INTO documents (content, language, search_vector) VALUES
    ('PostgreSQL database', 'english', to_tsvector('english', 'PostgreSQL database')),
    ('Base de datos PostgreSQL', 'spanish', to_tsvector('spanish', 'Base de datos PostgreSQL')),
    ('PostgreSQL Datenbank', 'german', to_tsvector('german', 'PostgreSQL Datenbank'));

-- Search specific language
SELECT content 
FROM documents
WHERE language = 'spanish'
  AND search_vector @@ to_tsquery('spanish', 'datos');

-- Search all languages
SELECT content, language
FROM documents
WHERE 
    (language = 'english' AND search_vector @@ to_tsquery('english', 'database'))
    OR (language = 'spanish' AND search_vector @@ to_tsquery('spanish', 'datos'))
    OR (language = 'german' AND search_vector @@ to_tsquery('german', 'datenbank'));
```

### Fuzzy Search

```sql
-- Install pg_trgm for fuzzy matching
CREATE EXTENSION pg_trgm;

-- Fuzzy text search
SELECT title, content
FROM articles
WHERE title % 'postgressql';  -- Similar to 'postgresql'

-- Combine FTS with fuzzy matching
SELECT 
    title,
    similarity(title, 'postgresql') as fuzzy_score,
    ts_rank(search_vector, query) as fts_score
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query
   OR title % 'postgresql'
ORDER BY fts_score DESC, fuzzy_score DESC;

-- GIN index for trigrams
CREATE INDEX idx_articles_title_trgm ON articles USING GIN(title gin_trgm_ops);
```

## Performance Optimization

### Index Maintenance

```sql
-- Vacuum FTS indexes regularly
VACUUM ANALYZE articles;

-- Rebuild bloated GIN index
REINDEX INDEX CONCURRENTLY idx_articles_search;

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexname LIKE '%search%'
ORDER BY idx_scan DESC;
```

### Query Optimization

```sql
-- Use covering indexes
CREATE INDEX idx_articles_search_covering 
ON articles USING GIN(search_vector) 
INCLUDE (title, created_at);

-- Materialize common queries
CREATE MATERIALIZED VIEW popular_articles AS
SELECT 
    id,
    title,
    ts_rank(search_vector, to_tsquery('english', 'postgresql')) as rank
FROM articles
WHERE search_vector @@ to_tsquery('english', 'postgresql')
ORDER BY rank DESC
LIMIT 100;

CREATE INDEX ON popular_articles (rank DESC);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY popular_articles;
```

### Partitioning for FTS

```sql
-- Partition by date for better performance
CREATE TABLE articles_partitioned (
    id SERIAL,
    title TEXT,
    content TEXT,
    created_at TIMESTAMP,
    search_vector tsvector
) PARTITION BY RANGE (created_at);

CREATE TABLE articles_2024 PARTITION OF articles_partitioned
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE INDEX ON articles_2024 USING GIN(search_vector);

-- Search only recent partitions
SELECT title FROM articles_2024
WHERE search_vector @@ to_tsquery('english', 'database')
  AND created_at > now() - interval '1 month';
```

## Best Practices

### 1. Choose Right Index Type

```sql
-- Read-heavy: Use GIN
CREATE INDEX idx_readonly_search ON readonly_articles USING GIN(search_vector);

-- Write-heavy: Use GiST
CREATE INDEX idx_writeactive_search ON active_articles USING GIST(search_vector);

-- Hybrid: Use both with partial indexes
CREATE INDEX idx_recent_gin ON articles USING GIN(search_vector)
WHERE created_at > now() - interval '90 days';

CREATE INDEX idx_archive_gist ON articles USING GIST(search_vector)
WHERE created_at <= now() - interval '90 days';
```

### 2. Use Appropriate Text Search Configuration

```sql
-- English content
ALTER TABLE articles ALTER COLUMN search_vector 
SET DEFAULT to_tsvector('english', '');

-- Simple (no stemming) for codes, identifiers
ALTER TABLE product_codes ALTER COLUMN search_vector 
SET DEFAULT to_tsvector('simple', '');

-- Custom configuration for domain-specific terms
CREATE TEXT SEARCH DICTIONARY tech_terms (
    TEMPLATE = synonym,
    SYNONYMS = tech_synonyms  -- Create synonym file
);
```

### 3. Monitor and Tune

```sql
-- Track search performance
CREATE TABLE search_analytics (
    id SERIAL PRIMARY KEY,
    query TEXT,
    results_count INTEGER,
    execution_time INTERVAL,
    searched_at TIMESTAMP DEFAULT now()
);

-- Log searches
CREATE FUNCTION log_search(search_query TEXT, result_count INTEGER, exec_time INTERVAL)
RETURNS VOID AS $$
BEGIN
    INSERT INTO search_analytics (query, results_count, execution_time)
    VALUES (search_query, result_count, exec_time);
END;
$$ LANGUAGE plpgsql;

-- Analyze search patterns
SELECT 
    query,
    count(*) as frequency,
    avg(results_count) as avg_results,
    avg(execution_time) as avg_time
FROM search_analytics
GROUP BY query
ORDER BY frequency DESC
LIMIT 20;
```

## Summary

PostgreSQL full-text search provides:
- **Text search types**: tsvector (documents) and tsquery (queries)
- **Linguistic features**: Stemming, stop words, multiple languages
- **Ranking**: Relevance scoring with customizable weights
- **Indexes**: GIN (fast reads) and GiST (fast updates)
- **Advanced features**: Highlighting, autocomplete, fuzzy search
- **Performance**: Optimization through indexes, partitioning, materialized views

Full-text search in PostgreSQL is powerful enough for most applications without external search engines.

## Next Steps

- Learn about [JSON and NoSQL Features](./26-json-and-nosql-features.md)
- Explore [Regular Expressions](./27-regular-expressions.md)
- Study [Index Optimization](./22-index-optimization.md)
- Practice [Performance Optimization](./20-query-optimization.md)
