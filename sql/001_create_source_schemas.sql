CREATE SCHEMA IF NOT EXISTS commerce;
CREATE SCHEMA IF NOT EXISTS crm;
CREATE SCHEMA IF NOT EXISTS marketing;
CREATE SCHEMA IF NOT EXISTS support;
CREATE SCHEMA IF NOT EXISTS ops;

CREATE TABLE IF NOT EXISTS commerce.customers (
 customer_id TEXT PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
 email TEXT, phone TEXT, city TEXT, country_code CHAR(2), created_at DATE NOT NULL,
 loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS commerce.orders (
 order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, order_date DATE NOT NULL,
 order_status TEXT NOT NULL, currency CHAR(3) NOT NULL,
 order_total NUMERIC(12,2) NOT NULL CHECK (order_total >= 0),
 loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_orders_customer ON commerce.orders(customer_id);
CREATE INDEX IF NOT EXISTS ix_orders_date ON commerce.orders(order_date);

CREATE TABLE IF NOT EXISTS crm.profiles (
 profile_id TEXT PRIMARY KEY, external_customer_ref TEXT NOT NULL,
 first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT, phone TEXT,
 postcode TEXT, updated_at TIMESTAMPTZ NOT NULL, loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_crm_external_ref ON crm.profiles(external_customer_ref);

CREATE TABLE IF NOT EXISTS marketing.events (
 event_id TEXT PRIMARY KEY, source_customer_ref TEXT NOT NULL, campaign_id TEXT NOT NULL,
 channel TEXT NOT NULL, event_type TEXT NOT NULL, event_timestamp TIMESTAMPTZ NOT NULL,
 loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_marketing_customer ON marketing.events(source_customer_ref);

CREATE TABLE IF NOT EXISTS support.tickets (
 ticket_id TEXT PRIMARY KEY, source_customer_ref TEXT NOT NULL, category TEXT NOT NULL,
 priority TEXT NOT NULL, status TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL,
 resolved_at TIMESTAMPTZ, loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_support_customer ON support.tickets(source_customer_ref);

CREATE TABLE IF NOT EXISTS ops.ingestion_runs (
 ingestion_run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 started_at TIMESTAMPTZ NOT NULL, finished_at TIMESTAMPTZ,
 status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
 row_counts JSONB NOT NULL DEFAULT '{}'::jsonb, error_message TEXT
);
