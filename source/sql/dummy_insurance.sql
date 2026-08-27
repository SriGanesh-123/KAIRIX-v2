-- ============================================================
-- DUMMY INSURANCE DATABASE SQL
-- Purpose: Sample SQL for parser / metadata extraction testing
-- ============================================================

CREATE SCHEMA IF NOT EXISTS insurance;

CREATE TABLE insurance.customer (
    customer_id      INTEGER PRIMARY KEY,
    customer_name    VARCHAR(100) NOT NULL,
    date_of_birth    DATE,
    email            VARCHAR(150),
    phone_number     VARCHAR(20),
    customer_status  VARCHAR(20) DEFAULT 'ACTIVE',
    created_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE insurance.policy (
    policy_id          INTEGER PRIMARY KEY,
    customer_id        INTEGER NOT NULL,
    policy_number      VARCHAR(50) UNIQUE NOT NULL,
    policy_type        VARCHAR(50) NOT NULL,
    policy_status      VARCHAR(20) DEFAULT 'ACTIVE',
    effective_date     DATE NOT NULL,
    expiration_date    DATE,
    written_premium    DECIMAL(15,2),
    coverage_limit     DECIMAL(15,2),
    CONSTRAINT fk_policy_customer
        FOREIGN KEY (customer_id)
        REFERENCES insurance.customer(customer_id),
    CONSTRAINT chk_policy_premium
        CHECK (written_premium >= 0),
    CONSTRAINT chk_policy_dates
        CHECK (expiration_date IS NULL OR expiration_date >= effective_date)
);

CREATE TABLE insurance.claim (
    claim_id          INTEGER PRIMARY KEY,
    policy_id         INTEGER NOT NULL,
    claim_number      VARCHAR(50) UNIQUE NOT NULL,
    claim_date        DATE NOT NULL,
    claim_amount      DECIMAL(15,2),
    approved_amount   DECIMAL(15,2),
    claim_status      VARCHAR(30) DEFAULT 'OPEN',
    CONSTRAINT fk_claim_policy
        FOREIGN KEY (policy_id)
        REFERENCES insurance.policy(policy_id),
    CONSTRAINT chk_claim_amount
        CHECK (claim_amount >= 0),
    CONSTRAINT chk_approved_amount
        CHECK (approved_amount IS NULL OR approved_amount >= 0)
);

CREATE TABLE insurance.payment (
    payment_id       INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL,
    payment_date     DATE NOT NULL,
    payment_amount   DECIMAL(15,2) NOT NULL,
    payment_type     VARCHAR(30),
    payment_status   VARCHAR(20) DEFAULT 'SUCCESS',
    CONSTRAINT fk_payment_policy
        FOREIGN KEY (policy_id)
        REFERENCES insurance.policy(policy_id),
    CONSTRAINT chk_payment_amount
        CHECK (payment_amount > 0)
);

CREATE TABLE insurance.premium_history (
    premium_id       INTEGER PRIMARY KEY,
    policy_id        INTEGER NOT NULL,
    premium_date     DATE NOT NULL,
    previous_premium DECIMAL(15,2),
    new_premium      DECIMAL(15,2),
    change_reason    VARCHAR(200),
    CONSTRAINT fk_premium_policy
        FOREIGN KEY (policy_id)
        REFERENCES insurance.policy(policy_id)
);

-- Sample data
INSERT INTO insurance.customer
    (customer_id, customer_name, date_of_birth, email, phone_number)
VALUES
    (1001, 'John Smith', '1985-04-12', 'john@example.com', '9876543210'),
    (1002, 'Mary Johnson', '1990-07-20', 'mary@example.com', '9876543211'),
    (1003, 'Robert Brown', '1978-11-05', 'robert@example.com', '9876543212');

INSERT INTO insurance.policy
    (policy_id, customer_id, policy_number, policy_type,
     policy_status, effective_date, expiration_date,
     written_premium, coverage_limit)
VALUES
    (5001, 1001, 'POL-10001', 'AUTO', 'ACTIVE',
     '2026-01-01', '2026-12-31', 12000.00, 500000.00),
    (5002, 1002, 'POL-10002', 'HOME', 'ACTIVE',
     '2026-02-01', '2027-01-31', 18000.00, 1000000.00),
    (5003, 1003, 'POL-10003', 'LIFE', 'ACTIVE',
     '2026-03-01', '2027-02-28', 25000.00, 2000000.00);

INSERT INTO insurance.claim
    (claim_id, policy_id, claim_number, claim_date,
     claim_amount, approved_amount, claim_status)
VALUES
    (9001, 5001, 'CLM-10001', '2026-05-10', 75000.00, 65000.00, 'APPROVED'),
    (9002, 5002, 'CLM-10002', '2026-06-15', 120000.00, 100000.00, 'APPROVED'),
    (9003, 5001, 'CLM-10003', '2026-07-20', 30000.00, NULL, 'OPEN');

INSERT INTO insurance.payment
    (payment_id, policy_id, payment_date, payment_amount,
     payment_type, payment_status)
VALUES
    (7001, 5001, '2026-01-05', 6000.00, 'PREMIUM', 'SUCCESS'),
    (7002, 5001, '2026-07-05', 6000.00, 'PREMIUM', 'SUCCESS'),
    (7003, 5002, '2026-02-05', 18000.00, 'PREMIUM', 'SUCCESS'),
    (7004, 5003, '2026-03-05', 25000.00, 'PREMIUM', 'SUCCESS');

-- Customer and policy join
SELECT
    c.customer_id,
    c.customer_name,
    p.policy_id,
    p.policy_number,
    p.policy_type,
    p.written_premium,
    p.policy_status
FROM insurance.customer c
INNER JOIN insurance.policy p
    ON c.customer_id = p.customer_id
WHERE p.policy_status = 'ACTIVE';

-- Policy claim summary
SELECT
    p.policy_id,
    p.policy_number,
    p.policy_type,
    p.written_premium,
    COUNT(cl.claim_id) AS claim_count,
    COALESCE(SUM(cl.claim_amount), 0) AS total_claim_amount,
    COALESCE(SUM(cl.approved_amount), 0) AS total_approved_amount
FROM insurance.policy p
LEFT JOIN insurance.claim cl
    ON p.policy_id = cl.policy_id
GROUP BY
    p.policy_id, p.policy_number, p.policy_type, p.written_premium;

-- Business Rule:
-- If approved claims exceed 50% of written premium,
-- increase the premium by 10%.
SELECT
    p.policy_id,
    p.policy_number,
    p.written_premium,
    COALESCE(SUM(cl.approved_amount), 0) AS approved_claims,
    CASE
        WHEN COALESCE(SUM(cl.approved_amount), 0)
             > (p.written_premium * 0.50)
        THEN p.written_premium * 1.10
        ELSE p.written_premium
    END AS calculated_premium
FROM insurance.policy p
LEFT JOIN insurance.claim cl
    ON p.policy_id = cl.policy_id
GROUP BY p.policy_id, p.policy_number, p.written_premium;

-- High-value claims
SELECT
    cl.claim_id,
    cl.claim_number,
    p.policy_number,
    c.customer_name,
    cl.claim_amount,
    cl.approved_amount,
    cl.claim_status
FROM insurance.claim cl
JOIN insurance.policy p
    ON cl.policy_id = p.policy_id
JOIN insurance.customer c
    ON p.customer_id = c.customer_id
WHERE cl.claim_amount > 50000
ORDER BY cl.claim_amount DESC;

-- Loss ratio
SELECT
    p.policy_id,
    p.policy_number,
    p.written_premium,
    COALESCE(SUM(cl.approved_amount), 0) AS approved_claims,
    CASE
        WHEN p.written_premium > 0
        THEN COALESCE(SUM(cl.approved_amount), 0)
             / p.written_premium * 100
        ELSE 0
    END AS loss_ratio_percentage
FROM insurance.policy p
LEFT JOIN insurance.claim cl
    ON p.policy_id = cl.policy_id
GROUP BY p.policy_id, p.policy_number, p.written_premium;

-- View
CREATE OR REPLACE VIEW insurance.policy_summary AS
SELECT
    p.policy_id,
    p.policy_number,
    c.customer_name,
    p.policy_type,
    p.policy_status,
    p.written_premium,
    p.coverage_limit,
    COALESCE(SUM(cl.claim_amount), 0) AS total_claim_amount,
    COALESCE(SUM(cl.approved_amount), 0) AS total_approved_claim_amount
FROM insurance.policy p
JOIN insurance.customer c
    ON p.customer_id = c.customer_id
LEFT JOIN insurance.claim cl
    ON p.policy_id = cl.policy_id
GROUP BY
    p.policy_id, p.policy_number, c.customer_name,
    p.policy_type, p.policy_status,
    p.written_premium, p.coverage_limit;

-- Update example
UPDATE insurance.policy
SET policy_status = 'EXPIRED'
WHERE expiration_date < CURRENT_DATE;

-- Delete example
DELETE FROM insurance.claim
WHERE claim_status = 'CANCELLED';

-- ETL-style transformation
INSERT INTO insurance.premium_history
    (premium_id, policy_id, premium_date,
     previous_premium, new_premium, change_reason)
SELECT
    ROW_NUMBER() OVER (ORDER BY p.policy_id) + 10000,
    p.policy_id,
    CURRENT_DATE,
    p.written_premium,
    CASE
        WHEN COALESCE(SUM(cl.approved_amount), 0)
             > p.written_premium * 0.50
        THEN p.written_premium * 1.10
        ELSE p.written_premium
    END,
    'Automated premium calculation'
FROM insurance.policy p
LEFT JOIN insurance.claim cl
    ON p.policy_id = cl.policy_id
GROUP BY p.policy_id, p.written_premium;

-- ============================================================
-- END OF DUMMY SQL FILE
-- ============================================================
