# Real-World Use Cases

## Overview

PostgreSQL powers applications across virtually every industry. This guide explores real-world implementations, demonstrating how PostgreSQL's features solve actual business problems with practical schemas, queries, and optimization strategies.

## Table of Contents
- [E-Commerce Platform](#e-commerce-platform)
- [Social Media Application](#social-media-application)
- [Financial Services](#financial-services)
- [Healthcare System](#healthcare-system)
- [Content Management System](#content-management-system)
- [IoT and Time-Series Data](#iot-and-time-series-data)
- [Geospatial Applications](#geospatial-applications)
- [Multi-Tenant SaaS](#multi-tenant-saas)
- [Analytics and Reporting](#analytics-and-reporting)
- [Real-Time Applications](#real-time-applications)

---

## E-Commerce Platform

### Schema Design

```sql
-- Core e-commerce schema
CREATE SCHEMA ecommerce;

-- Users and authentication
CREATE TABLE ecommerce.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted'))
);

-- Product catalog with full-text search
CREATE TABLE ecommerce.products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES ecommerce.categories(category_id),
    brand_id INTEGER REFERENCES ecommerce.brands(brand_id),
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    compare_at_price DECIMAL(10, 2),
    cost DECIMAL(10, 2),
    weight DECIMAL(10, 3),
    weight_unit VARCHAR(10) DEFAULT 'kg',
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    meta_title VARCHAR(255),
    meta_description TEXT,
    attributes JSONB DEFAULT '{}',
    search_vector TSVECTOR,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Product variants (size, color, etc.)
CREATE TABLE ecommerce.product_variants (
    variant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES ecommerce.products(product_id) ON DELETE CASCADE,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    price DECIMAL(10, 2),
    attributes JSONB NOT NULL DEFAULT '{}',
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    low_stock_threshold INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Inventory tracking
CREATE TABLE ecommerce.inventory (
    inventory_id SERIAL PRIMARY KEY,
    variant_id UUID REFERENCES ecommerce.product_variants(variant_id),
    warehouse_id INTEGER REFERENCES ecommerce.warehouses(warehouse_id),
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    UNIQUE (variant_id, warehouse_id),
    CHECK (quantity >= reserved_quantity)
);

-- Orders with status tracking
CREATE TABLE ecommerce.orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID REFERENCES ecommerce.users(user_id),
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    subtotal DECIMAL(12, 2) NOT NULL,
    tax_amount DECIMAL(12, 2) DEFAULT 0,
    shipping_amount DECIMAL(12, 2) DEFAULT 0,
    discount_amount DECIMAL(12, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    placed_at TIMESTAMPTZ DEFAULT NOW(),
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'confirmed', 'processing', 'shipped', 
        'delivered', 'cancelled', 'refunded'
    ))
);

-- Order items
CREATE TABLE ecommerce.order_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES ecommerce.orders(order_id) ON DELETE CASCADE,
    variant_id UUID REFERENCES ecommerce.product_variants(variant_id),
    product_name VARCHAR(255) NOT NULL,  -- Snapshot at time of order
    variant_name VARCHAR(255),
    sku VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(12, 2) NOT NULL,
    tax_rate DECIMAL(5, 4) DEFAULT 0,
    discount_amount DECIMAL(10, 2) DEFAULT 0
);

-- Shopping cart (session-based)
CREATE TABLE ecommerce.cart_items (
    cart_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(100) NOT NULL,
    user_id UUID REFERENCES ecommerce.users(user_id),
    variant_id UUID REFERENCES ecommerce.product_variants(variant_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    added_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (session_id, variant_id)
);
```

### Full-Text Search Implementation

```sql
-- Create search vector trigger
CREATE OR REPLACE FUNCTION ecommerce.update_product_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.sku, '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(
            (SELECT string_agg(value::text, ' ') FROM jsonb_each_text(NEW.attributes)), 
            ''
        )), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER product_search_update
    BEFORE INSERT OR UPDATE ON ecommerce.products
    FOR EACH ROW EXECUTE FUNCTION ecommerce.update_product_search_vector();

-- GIN index for fast search
CREATE INDEX idx_products_search ON ecommerce.products USING GIN(search_vector);

-- Search products
CREATE OR REPLACE FUNCTION ecommerce.search_products(
    search_query TEXT,
    category_filter INTEGER DEFAULT NULL,
    min_price DECIMAL DEFAULT NULL,
    max_price DECIMAL DEFAULT NULL,
    sort_by VARCHAR DEFAULT 'relevance',
    page_num INTEGER DEFAULT 1,
    page_size INTEGER DEFAULT 20
)
RETURNS TABLE (
    product_id UUID,
    name VARCHAR,
    price DECIMAL,
    category_id INTEGER,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.product_id,
        p.name,
        p.price,
        p.category_id,
        ts_rank(p.search_vector, websearch_to_tsquery('english', search_query)) AS relevance_score
    FROM ecommerce.products p
    WHERE p.is_active = TRUE
        AND (search_query IS NULL OR p.search_vector @@ websearch_to_tsquery('english', search_query))
        AND (category_filter IS NULL OR p.category_id = category_filter)
        AND (min_price IS NULL OR p.price >= min_price)
        AND (max_price IS NULL OR p.price <= max_price)
    ORDER BY 
        CASE WHEN sort_by = 'relevance' THEN 
            ts_rank(p.search_vector, websearch_to_tsquery('english', search_query)) END DESC NULLS LAST,
        CASE WHEN sort_by = 'price_asc' THEN p.price END ASC,
        CASE WHEN sort_by = 'price_desc' THEN p.price END DESC,
        CASE WHEN sort_by = 'newest' THEN p.created_at END DESC
    LIMIT page_size OFFSET (page_num - 1) * page_size;
END;
$$ LANGUAGE plpgsql;
```

### Inventory Management

```sql
-- Reserve inventory for order
CREATE OR REPLACE FUNCTION ecommerce.reserve_inventory(
    p_variant_id UUID,
    p_warehouse_id INTEGER,
    p_quantity INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    v_available INTEGER;
BEGIN
    -- Lock row for update
    SELECT quantity - reserved_quantity INTO v_available
    FROM ecommerce.inventory
    WHERE variant_id = p_variant_id AND warehouse_id = p_warehouse_id
    FOR UPDATE;
    
    IF v_available >= p_quantity THEN
        UPDATE ecommerce.inventory
        SET reserved_quantity = reserved_quantity + p_quantity
        WHERE variant_id = p_variant_id AND warehouse_id = p_warehouse_id;
        RETURN TRUE;
    ELSE
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Order placement with inventory
CREATE OR REPLACE FUNCTION ecommerce.place_order(
    p_user_id UUID,
    p_session_id VARCHAR,
    p_shipping_address JSONB,
    p_billing_address JSONB
)
RETURNS UUID AS $$
DECLARE
    v_order_id UUID;
    v_order_number VARCHAR(20);
    v_subtotal DECIMAL(12, 2);
    v_cart_item RECORD;
BEGIN
    -- Generate order number
    v_order_number := 'ORD-' || to_char(NOW(), 'YYYYMMDD') || '-' || 
                      lpad(nextval('ecommerce.order_number_seq')::TEXT, 6, '0');
    
    -- Calculate subtotal
    SELECT COALESCE(SUM(ci.quantity * COALESCE(pv.price, p.price)), 0) INTO v_subtotal
    FROM ecommerce.cart_items ci
    JOIN ecommerce.product_variants pv ON ci.variant_id = pv.variant_id
    JOIN ecommerce.products p ON pv.product_id = p.product_id
    WHERE ci.session_id = p_session_id;
    
    IF v_subtotal = 0 THEN
        RAISE EXCEPTION 'Cart is empty';
    END IF;
    
    -- Create order
    INSERT INTO ecommerce.orders (
        order_number, user_id, subtotal, total_amount,
        shipping_address, billing_address
    ) VALUES (
        v_order_number, p_user_id, v_subtotal, v_subtotal,
        p_shipping_address, p_billing_address
    ) RETURNING order_id INTO v_order_id;
    
    -- Move cart items to order items
    INSERT INTO ecommerce.order_items (
        order_id, variant_id, product_name, variant_name, sku,
        quantity, unit_price, total_price
    )
    SELECT 
        v_order_id,
        ci.variant_id,
        p.name,
        pv.name,
        pv.sku,
        ci.quantity,
        COALESCE(pv.price, p.price),
        ci.quantity * COALESCE(pv.price, p.price)
    FROM ecommerce.cart_items ci
    JOIN ecommerce.product_variants pv ON ci.variant_id = pv.variant_id
    JOIN ecommerce.products p ON pv.product_id = p.product_id
    WHERE ci.session_id = p_session_id;
    
    -- Clear cart
    DELETE FROM ecommerce.cart_items WHERE session_id = p_session_id;
    
    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;
```

### Analytics Queries

```sql
-- Sales dashboard
CREATE VIEW ecommerce.sales_dashboard AS
SELECT 
    DATE_TRUNC('day', o.placed_at) AS date,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.user_id) AS unique_customers,
    SUM(o.total_amount) AS revenue,
    AVG(o.total_amount) AS avg_order_value,
    SUM(oi.quantity) AS items_sold
FROM ecommerce.orders o
JOIN ecommerce.order_items oi ON o.order_id = oi.order_id
WHERE o.status NOT IN ('cancelled', 'refunded')
GROUP BY DATE_TRUNC('day', o.placed_at);

-- Top selling products
SELECT 
    p.product_id,
    p.name,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.total_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count
FROM ecommerce.products p
JOIN ecommerce.product_variants pv ON p.product_id = pv.product_id
JOIN ecommerce.order_items oi ON pv.variant_id = oi.variant_id
JOIN ecommerce.orders o ON oi.order_id = o.order_id
WHERE o.placed_at >= NOW() - INTERVAL '30 days'
    AND o.status NOT IN ('cancelled', 'refunded')
GROUP BY p.product_id, p.name
ORDER BY revenue DESC
LIMIT 10;

-- Customer lifetime value
SELECT 
    u.user_id,
    u.email,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.total_amount) AS lifetime_value,
    MIN(o.placed_at) AS first_order,
    MAX(o.placed_at) AS last_order,
    AVG(o.total_amount) AS avg_order_value
FROM ecommerce.users u
JOIN ecommerce.orders o ON u.user_id = o.user_id
WHERE o.status NOT IN ('cancelled', 'refunded')
GROUP BY u.user_id, u.email
ORDER BY lifetime_value DESC;
```

---

## Social Media Application

### Schema Design

```sql
CREATE SCHEMA social;

-- User profiles
CREATE TABLE social.users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    bio TEXT,
    avatar_url TEXT,
    cover_image_url TEXT,
    location VARCHAR(100),
    website VARCHAR(255),
    birth_date DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    follower_count INTEGER DEFAULT 0,
    following_count INTEGER DEFAULT 0,
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Posts (tweets, status updates)
CREATE TABLE social.posts (
    post_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    content TEXT NOT NULL CHECK (char_length(content) <= 280),
    media_urls TEXT[],
    reply_to_id UUID REFERENCES social.posts(post_id) ON DELETE SET NULL,
    repost_of_id UUID REFERENCES social.posts(post_id) ON DELETE SET NULL,
    quote_of_id UUID REFERENCES social.posts(post_id) ON DELETE SET NULL,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    repost_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    is_pinned BOOLEAN DEFAULT FALSE,
    visibility VARCHAR(20) DEFAULT 'public',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    search_vector TSVECTOR
);

-- User relationships (follow/block)
CREATE TABLE social.user_relationships (
    follower_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    following_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    relationship_type VARCHAR(20) NOT NULL DEFAULT 'follow',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (follower_id, following_id),
    CHECK (follower_id != following_id),
    CHECK (relationship_type IN ('follow', 'block', 'mute'))
);

-- Likes
CREATE TABLE social.likes (
    user_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    post_id UUID REFERENCES social.posts(post_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, post_id)
);

-- Hashtags
CREATE TABLE social.hashtags (
    hashtag_id SERIAL PRIMARY KEY,
    tag VARCHAR(100) UNIQUE NOT NULL,
    post_count INTEGER DEFAULT 0,
    first_used_at TIMESTAMPTZ DEFAULT NOW(),
    last_used_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE social.post_hashtags (
    post_id UUID REFERENCES social.posts(post_id) ON DELETE CASCADE,
    hashtag_id INTEGER REFERENCES social.hashtags(hashtag_id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, hashtag_id)
);

-- Notifications
CREATE TABLE social.notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    actor_id UUID REFERENCES social.users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(30) NOT NULL,
    target_type VARCHAR(30),
    target_id UUID,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### News Feed Algorithm

```sql
-- Generate personalized feed
CREATE OR REPLACE FUNCTION social.get_user_feed(
    p_user_id UUID,
    p_cursor TIMESTAMPTZ DEFAULT NULL,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    post_id UUID,
    user_id UUID,
    username VARCHAR,
    display_name VARCHAR,
    avatar_url TEXT,
    content TEXT,
    media_urls TEXT[],
    like_count INTEGER,
    reply_count INTEGER,
    repost_count INTEGER,
    created_at TIMESTAMPTZ,
    is_liked BOOLEAN,
    is_reposted BOOLEAN,
    feed_reason VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH following AS (
        -- Users being followed
        SELECT following_id 
        FROM social.user_relationships 
        WHERE follower_id = p_user_id AND relationship_type = 'follow'
    ),
    blocked AS (
        -- Users blocked by or blocking this user
        SELECT CASE 
            WHEN follower_id = p_user_id THEN following_id 
            ELSE follower_id 
        END AS blocked_user_id
        FROM social.user_relationships 
        WHERE (follower_id = p_user_id OR following_id = p_user_id)
            AND relationship_type = 'block'
    ),
    feed_posts AS (
        -- Own posts
        SELECT p.post_id, p.user_id, p.content, p.media_urls, 
               p.like_count, p.reply_count, p.repost_count, 
               p.created_at, 'own_post'::VARCHAR AS feed_reason,
               1 AS priority
        FROM social.posts p
        WHERE p.user_id = p_user_id
            AND p.reply_to_id IS NULL
            AND (p_cursor IS NULL OR p.created_at < p_cursor)
        
        UNION ALL
        
        -- Posts from followed users
        SELECT p.post_id, p.user_id, p.content, p.media_urls,
               p.like_count, p.reply_count, p.repost_count,
               p.created_at, 'following'::VARCHAR AS feed_reason,
               2 AS priority
        FROM social.posts p
        JOIN following f ON p.user_id = f.following_id
        WHERE p.reply_to_id IS NULL
            AND p.visibility = 'public'
            AND p.user_id NOT IN (SELECT blocked_user_id FROM blocked)
            AND (p_cursor IS NULL OR p.created_at < p_cursor)
        
        UNION ALL
        
        -- Posts liked by followed users (engagement-based)
        SELECT p.post_id, p.user_id, p.content, p.media_urls,
               p.like_count, p.reply_count, p.repost_count,
               l.created_at, 'liked_by_following'::VARCHAR AS feed_reason,
               3 AS priority
        FROM social.likes l
        JOIN following f ON l.user_id = f.following_id
        JOIN social.posts p ON l.post_id = p.post_id
        WHERE p.reply_to_id IS NULL
            AND p.visibility = 'public'
            AND p.user_id NOT IN (SELECT blocked_user_id FROM blocked)
            AND p.user_id != p_user_id
            AND (p_cursor IS NULL OR l.created_at < p_cursor)
    )
    SELECT DISTINCT ON (fp.post_id)
        fp.post_id,
        fp.user_id,
        u.username,
        u.display_name,
        u.avatar_url,
        fp.content,
        fp.media_urls,
        fp.like_count,
        fp.reply_count,
        fp.repost_count,
        fp.created_at,
        EXISTS(SELECT 1 FROM social.likes WHERE user_id = p_user_id AND post_id = fp.post_id) AS is_liked,
        EXISTS(SELECT 1 FROM social.posts WHERE user_id = p_user_id AND repost_of_id = fp.post_id) AS is_reposted,
        fp.feed_reason
    FROM feed_posts fp
    JOIN social.users u ON fp.user_id = u.user_id
    ORDER BY fp.post_id, fp.priority, fp.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

### Trending Topics

```sql
-- Calculate trending hashtags
CREATE OR REPLACE FUNCTION social.get_trending_hashtags(
    p_hours INTEGER DEFAULT 24,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    hashtag_id INTEGER,
    tag VARCHAR,
    post_count BIGINT,
    growth_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH recent_counts AS (
        SELECT 
            ph.hashtag_id,
            COUNT(*) AS recent_count
        FROM social.post_hashtags ph
        JOIN social.posts p ON ph.post_id = p.post_id
        WHERE p.created_at > NOW() - (p_hours || ' hours')::INTERVAL
        GROUP BY ph.hashtag_id
    ),
    previous_counts AS (
        SELECT 
            ph.hashtag_id,
            COUNT(*) AS previous_count
        FROM social.post_hashtags ph
        JOIN social.posts p ON ph.post_id = p.post_id
        WHERE p.created_at BETWEEN 
            NOW() - (p_hours * 2 || ' hours')::INTERVAL 
            AND NOW() - (p_hours || ' hours')::INTERVAL
        GROUP BY ph.hashtag_id
    )
    SELECT 
        h.hashtag_id,
        h.tag,
        rc.recent_count AS post_count,
        CASE 
            WHEN COALESCE(pc.previous_count, 0) = 0 THEN rc.recent_count::NUMERIC
            ELSE (rc.recent_count - COALESCE(pc.previous_count, 0))::NUMERIC / 
                 COALESCE(pc.previous_count, 1)::NUMERIC * 100
        END AS growth_rate
    FROM recent_counts rc
    JOIN social.hashtags h ON rc.hashtag_id = h.hashtag_id
    LEFT JOIN previous_counts pc ON rc.hashtag_id = pc.hashtag_id
    WHERE rc.recent_count >= 5  -- Minimum threshold
    ORDER BY growth_rate DESC, rc.recent_count DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

---

## Financial Services

### Schema Design

```sql
CREATE SCHEMA banking;

-- Accounts
CREATE TABLE banking.accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_number VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID NOT NULL,
    account_type VARCHAR(30) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    balance DECIMAL(15, 2) DEFAULT 0 CHECK (balance >= 0),
    available_balance DECIMAL(15, 2) DEFAULT 0,
    credit_limit DECIMAL(15, 2) DEFAULT 0,
    interest_rate DECIMAL(5, 4) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active',
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    CONSTRAINT valid_account_type CHECK (account_type IN (
        'checking', 'savings', 'credit', 'loan', 'investment'
    ))
);

-- Transactions with double-entry bookkeeping
CREATE TABLE banking.transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_number VARCHAR(30) UNIQUE NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    description TEXT,
    total_amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',
    initiated_by UUID,
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

-- Transaction entries (double-entry)
CREATE TABLE banking.transaction_entries (
    entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID REFERENCES banking.transactions(transaction_id),
    account_id UUID REFERENCES banking.accounts(account_id),
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    balance_after DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scheduled transfers
CREATE TABLE banking.scheduled_transfers (
    schedule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_account_id UUID REFERENCES banking.accounts(account_id),
    to_account_id UUID REFERENCES banking.accounts(account_id),
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    frequency VARCHAR(20) NOT NULL,
    next_execution_date DATE NOT NULL,
    last_execution_date DATE,
    end_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log
CREATE TABLE banking.audit_log (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by UUID,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);
```

### Secure Transfer Function

```sql
-- Transfer money between accounts (ACID compliant)
CREATE OR REPLACE FUNCTION banking.transfer_money(
    p_from_account_id UUID,
    p_to_account_id UUID,
    p_amount DECIMAL(15, 2),
    p_description TEXT DEFAULT NULL,
    p_initiated_by UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_transaction_id UUID;
    v_reference_number VARCHAR(30);
    v_from_balance DECIMAL(15, 2);
    v_to_balance DECIMAL(15, 2);
    v_from_account RECORD;
    v_to_account RECORD;
BEGIN
    -- Validate amount
    IF p_amount <= 0 THEN
        RAISE EXCEPTION 'Transfer amount must be positive';
    END IF;
    
    -- Lock accounts in consistent order to prevent deadlocks
    SELECT * INTO v_from_account 
    FROM banking.accounts 
    WHERE account_id = LEAST(p_from_account_id, p_to_account_id)
    FOR UPDATE;
    
    SELECT * INTO v_to_account 
    FROM banking.accounts 
    WHERE account_id = GREATEST(p_from_account_id, p_to_account_id)
    FOR UPDATE;
    
    -- Reassign based on actual IDs
    IF v_from_account.account_id != p_from_account_id THEN
        v_from_account := v_to_account;
        SELECT * INTO v_to_account FROM banking.accounts 
        WHERE account_id = p_to_account_id FOR UPDATE;
    END IF;
    
    -- Validate accounts
    IF v_from_account.status != 'active' THEN
        RAISE EXCEPTION 'Source account is not active';
    END IF;
    IF v_to_account.status != 'active' THEN
        RAISE EXCEPTION 'Destination account is not active';
    END IF;
    
    -- Check sufficient funds
    IF v_from_account.available_balance < p_amount THEN
        RAISE EXCEPTION 'Insufficient funds. Available: %, Required: %', 
            v_from_account.available_balance, p_amount;
    END IF;
    
    -- Generate reference number
    v_reference_number := 'TRF' || to_char(NOW(), 'YYYYMMDDHH24MISS') || 
                          lpad(floor(random() * 10000)::TEXT, 4, '0');
    
    -- Create transaction record
    INSERT INTO banking.transactions (
        reference_number, transaction_type, description, total_amount, 
        status, initiated_by, completed_at
    ) VALUES (
        v_reference_number, 'transfer', p_description, p_amount,
        'completed', p_initiated_by, NOW()
    ) RETURNING transaction_id INTO v_transaction_id;
    
    -- Debit source account
    UPDATE banking.accounts
    SET balance = balance - p_amount,
        available_balance = available_balance - p_amount
    WHERE account_id = p_from_account_id
    RETURNING balance INTO v_from_balance;
    
    INSERT INTO banking.transaction_entries (
        transaction_id, account_id, entry_type, amount, balance_after
    ) VALUES (
        v_transaction_id, p_from_account_id, 'debit', p_amount, v_from_balance
    );
    
    -- Credit destination account
    UPDATE banking.accounts
    SET balance = balance + p_amount,
        available_balance = available_balance + p_amount
    WHERE account_id = p_to_account_id
    RETURNING balance INTO v_to_balance;
    
    INSERT INTO banking.transaction_entries (
        transaction_id, account_id, entry_type, amount, balance_after
    ) VALUES (
        v_transaction_id, p_to_account_id, 'credit', p_amount, v_to_balance
    );
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;
```

### Account Statement

```sql
-- Generate account statement
CREATE OR REPLACE FUNCTION banking.get_account_statement(
    p_account_id UUID,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    date DATE,
    reference_number VARCHAR,
    description TEXT,
    debit DECIMAL,
    credit DECIMAL,
    balance DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH entries AS (
        SELECT 
            te.created_at::DATE AS entry_date,
            t.reference_number,
            t.description,
            CASE WHEN te.entry_type = 'debit' THEN te.amount ELSE NULL END AS debit,
            CASE WHEN te.entry_type = 'credit' THEN te.amount ELSE NULL END AS credit,
            te.balance_after,
            te.created_at
        FROM banking.transaction_entries te
        JOIN banking.transactions t ON te.transaction_id = t.transaction_id
        WHERE te.account_id = p_account_id
            AND te.created_at::DATE BETWEEN p_start_date AND p_end_date
            AND t.status = 'completed'
    )
    SELECT 
        e.entry_date,
        e.reference_number,
        e.description,
        e.debit,
        e.credit,
        e.balance_after
    FROM entries e
    ORDER BY e.created_at;
END;
$$ LANGUAGE plpgsql;
```

---

## Healthcare System

### Schema Design

```sql
CREATE SCHEMA healthcare;

-- Patients
CREATE TABLE healthcare.patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(20) UNIQUE NOT NULL,  -- Medical Record Number
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    blood_type VARCHAR(5),
    ssn_hash VARCHAR(64),  -- Hashed for security
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    emergency_contact JSONB,
    address JSONB,
    insurance_info JSONB,
    allergies TEXT[],
    chronic_conditions TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Healthcare providers
CREATE TABLE healthcare.providers (
    provider_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    npi VARCHAR(10) UNIQUE NOT NULL,  -- National Provider Identifier
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    department VARCHAR(100),
    license_number VARCHAR(50),
    license_state VARCHAR(2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Appointments
CREATE TABLE healthcare.appointments (
    appointment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES healthcare.patients(patient_id),
    provider_id UUID REFERENCES healthcare.providers(provider_id),
    appointment_type VARCHAR(50) NOT NULL,
    scheduled_start TIMESTAMPTZ NOT NULL,
    scheduled_end TIMESTAMPTZ NOT NULL,
    actual_start TIMESTAMPTZ,
    actual_end TIMESTAMPTZ,
    status VARCHAR(30) DEFAULT 'scheduled',
    reason_for_visit TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT no_overlap EXCLUDE USING GIST (
        provider_id WITH =,
        tstzrange(scheduled_start, scheduled_end) WITH &&
    ) WHERE (status NOT IN ('cancelled', 'no_show'))
);

-- Medical encounters/visits
CREATE TABLE healthcare.encounters (
    encounter_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES healthcare.patients(patient_id),
    provider_id UUID REFERENCES healthcare.providers(provider_id),
    appointment_id UUID REFERENCES healthcare.appointments(appointment_id),
    encounter_type VARCHAR(50) NOT NULL,
    encounter_date TIMESTAMPTZ NOT NULL,
    chief_complaint TEXT,
    diagnosis_codes VARCHAR(10)[],  -- ICD-10 codes
    procedure_codes VARCHAR(10)[],  -- CPT codes
    vitals JSONB,
    examination_notes TEXT,
    assessment TEXT,
    plan TEXT,
    follow_up_instructions TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prescriptions
CREATE TABLE healthcare.prescriptions (
    prescription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encounter_id UUID REFERENCES healthcare.encounters(encounter_id),
    patient_id UUID REFERENCES healthcare.patients(patient_id),
    provider_id UUID REFERENCES healthcare.providers(provider_id),
    medication_name VARCHAR(255) NOT NULL,
    medication_code VARCHAR(20),  -- NDC code
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    route VARCHAR(50),
    duration VARCHAR(100),
    quantity INTEGER,
    refills_allowed INTEGER DEFAULT 0,
    refills_remaining INTEGER DEFAULT 0,
    instructions TEXT,
    prescribed_at TIMESTAMPTZ DEFAULT NOW(),
    start_date DATE,
    end_date DATE,
    status VARCHAR(30) DEFAULT 'active'
);

-- Lab results
CREATE TABLE healthcare.lab_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES healthcare.patients(patient_id),
    encounter_id UUID REFERENCES healthcare.encounters(encounter_id),
    ordered_by UUID REFERENCES healthcare.providers(provider_id),
    test_code VARCHAR(20) NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    specimen_type VARCHAR(50),
    collected_at TIMESTAMPTZ,
    resulted_at TIMESTAMPTZ,
    results JSONB NOT NULL,  -- Flexible for different test types
    reference_range JSONB,
    interpretation VARCHAR(50),
    is_abnormal BOOLEAN DEFAULT FALSE,
    notes TEXT,
    status VARCHAR(30) DEFAULT 'pending'
);
```

### HIPAA-Compliant Audit Logging

```sql
-- Audit trigger for sensitive tables
CREATE OR REPLACE FUNCTION healthcare.audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        INSERT INTO healthcare.audit_log (
            table_name, record_id, action, old_values, new_values,
            changed_by, ip_address
        ) VALUES (
            TG_TABLE_NAME, 
            NEW.patient_id,
            'UPDATE',
            v_old_data,
            v_new_data,
            current_setting('app.current_user_id', TRUE)::UUID,
            current_setting('app.client_ip', TRUE)::INET
        );
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        v_old_data := to_jsonb(OLD);
        INSERT INTO healthcare.audit_log (
            table_name, record_id, action, old_values,
            changed_by, ip_address
        ) VALUES (
            TG_TABLE_NAME,
            OLD.patient_id,
            'DELETE',
            v_old_data,
            current_setting('app.current_user_id', TRUE)::UUID,
            current_setting('app.client_ip', TRUE)::INET
        );
        RETURN OLD;
    ELSIF (TG_OP = 'INSERT') THEN
        v_new_data := to_jsonb(NEW);
        INSERT INTO healthcare.audit_log (
            table_name, record_id, action, new_values,
            changed_by, ip_address
        ) VALUES (
            TG_TABLE_NAME,
            NEW.patient_id,
            'INSERT',
            v_new_data,
            current_setting('app.current_user_id', TRUE)::UUID,
            current_setting('app.client_ip', TRUE)::INET
        );
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply to sensitive tables
CREATE TRIGGER patients_audit
    AFTER INSERT OR UPDATE OR DELETE ON healthcare.patients
    FOR EACH ROW EXECUTE FUNCTION healthcare.audit_trigger_func();
```

### Patient Timeline Query

```sql
-- Complete patient medical history
CREATE OR REPLACE FUNCTION healthcare.get_patient_timeline(
    p_patient_id UUID,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    event_date TIMESTAMPTZ,
    event_type VARCHAR,
    summary TEXT,
    details JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM (
        -- Encounters
        SELECT 
            e.encounter_date AS event_date,
            'Encounter'::VARCHAR AS event_type,
            e.encounter_type || ': ' || COALESCE(e.chief_complaint, '') AS summary,
            jsonb_build_object(
                'provider', p.first_name || ' ' || p.last_name,
                'diagnosis', e.diagnosis_codes,
                'procedures', e.procedure_codes
            ) AS details
        FROM healthcare.encounters e
        JOIN healthcare.providers p ON e.provider_id = p.provider_id
        WHERE e.patient_id = p_patient_id
        
        UNION ALL
        
        -- Prescriptions
        SELECT 
            pr.prescribed_at AS event_date,
            'Prescription'::VARCHAR AS event_type,
            pr.medication_name || ' - ' || pr.dosage AS summary,
            jsonb_build_object(
                'frequency', pr.frequency,
                'duration', pr.duration,
                'provider', pv.first_name || ' ' || pv.last_name
            ) AS details
        FROM healthcare.prescriptions pr
        JOIN healthcare.providers pv ON pr.provider_id = pv.provider_id
        WHERE pr.patient_id = p_patient_id
        
        UNION ALL
        
        -- Lab results
        SELECT 
            lr.resulted_at AS event_date,
            'Lab Result'::VARCHAR AS event_type,
            lr.test_name || CASE WHEN lr.is_abnormal THEN ' (ABNORMAL)' ELSE '' END AS summary,
            jsonb_build_object(
                'results', lr.results,
                'reference_range', lr.reference_range,
                'interpretation', lr.interpretation
            ) AS details
        FROM healthcare.lab_results lr
        WHERE lr.patient_id = p_patient_id AND lr.status = 'completed'
    ) timeline
    ORDER BY event_date DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

---

## IoT and Time-Series Data

### Schema with TimescaleDB

```sql
-- Note: Requires TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Devices
CREATE TABLE iot.devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_type VARCHAR(50) NOT NULL,
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    firmware_version VARCHAR(20),
    location_id INTEGER,
    location_name VARCHAR(255),
    coordinates POINT,
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    last_seen_at TIMESTAMPTZ,
    registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sensor readings (hypertable)
CREATE TABLE iot.sensor_readings (
    time TIMESTAMPTZ NOT NULL,
    device_id UUID NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    quality_score SMALLINT DEFAULT 100,
    metadata JSONB
);

-- Convert to hypertable (TimescaleDB)
SELECT create_hypertable('iot.sensor_readings', 'time', 
    chunk_time_interval => INTERVAL '1 day');

-- Enable compression for older data
ALTER TABLE iot.sensor_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'device_id, sensor_type',
    timescaledb.compress_orderby = 'time DESC'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('iot.sensor_readings', INTERVAL '7 days');

-- Retention policy (delete data older than 1 year)
SELECT add_retention_policy('iot.sensor_readings', INTERVAL '1 year');

-- Continuous aggregates for hourly rollups
CREATE MATERIALIZED VIEW iot.sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    device_id,
    sensor_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS reading_count
FROM iot.sensor_readings
GROUP BY time_bucket('1 hour', time), device_id, sensor_type;

-- Refresh policy for continuous aggregate
SELECT add_continuous_aggregate_policy('iot.sensor_readings_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Alerts/anomalies
CREATE TABLE iot.alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES iot.devices(device_id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    reading_time TIMESTAMPTZ,
    reading_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    acknowledged_at TIMESTAMPTZ,
    acknowledged_by UUID,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Real-Time Analytics Queries

```sql
-- Last reading for all devices
SELECT DISTINCT ON (device_id, sensor_type)
    device_id,
    sensor_type,
    time,
    value
FROM iot.sensor_readings
ORDER BY device_id, sensor_type, time DESC;

-- Devices with no recent readings (potentially offline)
SELECT 
    d.device_id,
    d.serial_number,
    d.device_type,
    d.last_seen_at,
    NOW() - d.last_seen_at AS time_since_last_seen
FROM iot.devices d
WHERE d.is_active = TRUE
    AND d.last_seen_at < NOW() - INTERVAL '5 minutes'
ORDER BY d.last_seen_at;

-- Hourly averages for dashboard
SELECT 
    bucket,
    device_id,
    sensor_type,
    avg_value,
    min_value,
    max_value
FROM iot.sensor_readings_hourly
WHERE bucket >= NOW() - INTERVAL '24 hours'
    AND device_id = 'your-device-id'
ORDER BY bucket DESC;

-- Anomaly detection (values outside 3 standard deviations)
WITH stats AS (
    SELECT 
        device_id,
        sensor_type,
        AVG(value) AS mean_value,
        STDDEV(value) AS std_value
    FROM iot.sensor_readings
    WHERE time >= NOW() - INTERVAL '7 days'
    GROUP BY device_id, sensor_type
)
SELECT 
    r.time,
    r.device_id,
    r.sensor_type,
    r.value,
    s.mean_value,
    ABS(r.value - s.mean_value) / NULLIF(s.std_value, 0) AS z_score
FROM iot.sensor_readings r
JOIN stats s ON r.device_id = s.device_id AND r.sensor_type = s.sensor_type
WHERE r.time >= NOW() - INTERVAL '1 hour'
    AND ABS(r.value - s.mean_value) > 3 * s.std_value
ORDER BY r.time DESC;
```

---

## Geospatial Applications

### Schema with PostGIS

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE SCHEMA geo;

-- Points of Interest
CREATE TABLE geo.points_of_interest (
    poi_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    subcategory VARCHAR(50),
    description TEXT,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    attributes JSONB DEFAULT '{}',
    rating DECIMAL(3, 2),
    review_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Spatial index
CREATE INDEX idx_poi_location ON geo.points_of_interest USING GIST(location);

-- Service areas (polygons)
CREATE TABLE geo.service_areas (
    area_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    service_type VARCHAR(50),
    boundary GEOGRAPHY(POLYGON, 4326) NOT NULL,
    properties JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_service_areas_boundary ON geo.service_areas USING GIST(boundary);

-- Routes/paths
CREATE TABLE geo.routes (
    route_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    route_type VARCHAR(50),
    path GEOGRAPHY(LINESTRING, 4326) NOT NULL,
    distance_meters DOUBLE PRECISION,
    estimated_duration_seconds INTEGER,
    waypoints JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Geospatial Queries

```sql
-- Find nearby points of interest
CREATE OR REPLACE FUNCTION geo.find_nearby_pois(
    p_latitude DOUBLE PRECISION,
    p_longitude DOUBLE PRECISION,
    p_radius_meters INTEGER DEFAULT 1000,
    p_category VARCHAR DEFAULT NULL,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    poi_id UUID,
    name VARCHAR,
    category VARCHAR,
    distance_meters DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.poi_id,
        p.name,
        p.category,
        ST_Distance(p.location, ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography) AS distance_meters,
        ST_Y(p.location::geometry) AS latitude,
        ST_X(p.location::geometry) AS longitude
    FROM geo.points_of_interest p
    WHERE ST_DWithin(
        p.location,
        ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography,
        p_radius_meters
    )
    AND (p_category IS NULL OR p.category = p_category)
    ORDER BY distance_meters
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Check if point is within service area
SELECT 
    sa.name AS service_area,
    sa.service_type
FROM geo.service_areas sa
WHERE ST_Within(
    ST_SetSRID(ST_MakePoint(-122.4194, 37.7749), 4326)::geography,
    sa.boundary
)
AND sa.is_active = TRUE;

-- Calculate route distance
SELECT 
    route_id,
    name,
    ST_Length(path) AS distance_meters
FROM geo.routes
WHERE route_type = 'delivery';

-- Find POIs along a route (within buffer)
SELECT p.*
FROM geo.points_of_interest p
JOIN geo.routes r ON ST_DWithin(p.location, r.path, 100)  -- 100 meters buffer
WHERE r.route_id = 'your-route-id';
```

---

## Multi-Tenant SaaS

### Schema Per Tenant

```sql
-- Tenant management in shared schema
CREATE SCHEMA shared;

CREATE TABLE shared.tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(50) DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Function to create tenant schema
CREATE OR REPLACE FUNCTION shared.create_tenant_schema(p_tenant_slug VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_schema_name VARCHAR;
BEGIN
    v_schema_name := 'tenant_' || p_tenant_slug;
    
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', v_schema_name);
    
    -- Create tenant-specific tables
    EXECUTE format('
        CREATE TABLE %I.users (
            user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(100),
            role VARCHAR(50) DEFAULT ''user'',
            created_at TIMESTAMPTZ DEFAULT NOW()
        )', v_schema_name);
    
    EXECUTE format('
        CREATE TABLE %I.projects (
            project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            owner_id UUID REFERENCES %I.users(user_id),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )', v_schema_name, v_schema_name);
    
    -- Add more tables as needed
END;
$$ LANGUAGE plpgsql;
```

### Row-Level Security Multi-Tenancy

```sql
-- Shared table with tenant column
CREATE TABLE saas.projects (
    project_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES shared.tenants(tenant_id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE saas.projects ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON saas.projects
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Function to set tenant context
CREATE OR REPLACE FUNCTION shared.set_tenant_context(p_tenant_id UUID)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', p_tenant_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql;
```

---

## Summary

### Key Takeaways

| Use Case | Key PostgreSQL Features |
|----------|------------------------|
| E-Commerce | JSONB, Full-text search, Transactions |
| Social Media | CTEs, Window functions, Arrays |
| Financial | ACID compliance, Triggers, Audit logging |
| Healthcare | RLS, Encryption, Audit trails |
| IoT/Time-Series | TimescaleDB, Partitioning, Continuous aggregates |
| Geospatial | PostGIS, Spatial indexes, Geography types |
| Multi-Tenant | Schemas, RLS, Search paths |

### Best Practices

1. **Design for your workload**: OLTP vs OLAP considerations
2. **Use appropriate data types**: JSONB, Arrays, specialized types
3. **Implement proper indexes**: B-tree, GIN, GiST, BRIN
4. **Leverage PostgreSQL extensions**: TimescaleDB, PostGIS, pg_trgm
5. **Ensure data integrity**: Constraints, triggers, transactions
6. **Plan for scale**: Partitioning, connection pooling, replication

---

## Next Steps

- [Common Patterns and Anti-Patterns](50-patterns-and-antipatterns.md)
- [Migration Strategies](51-migration-strategies.md)
- [Troubleshooting Guide](52-troubleshooting-guide.md)
