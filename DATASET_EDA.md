# 📊 Dataset Description & Exploratory Data Analysis (EDA)

This document describes the data structures, schemas, and analysis of the datasets used in the Agentic Fraud Detection System.

---

## 📋 Table of Contents

1. [Dataset Overview](#1-dataset-overview)
2. [Transaction Schema](#2-transaction-schema)
3. [Customer Profile Schema](#3-customer-profile-schema)
4. [Velocity Context Schema](#4-velocity-context-schema)
5. [Fraud Decision Schema](#5-fraud-decision-schema)
6. [Demo Scenarios Data](#6-demo-scenarios-data)
7. [EDA: Statistical Summary](#7-eda-statistical-summary)
8. [EDA: Fraud Patterns](#8-eda-fraud-patterns)
9. [Detection Thresholds](#9-detection-thresholds)

---

## 1. Dataset Overview

The system uses **synthetic data** generated for fraud detection simulation. There are 4 main data entities:

| Dataset | Storage | Purpose |
|---------|---------|---------|
| **Transactions** | Kafka Topic + KTable | Real-time transaction stream |
| **Customer Profiles** | KTable (RocksDB) | Customer baselines for comparison |
| **Velocity Context** | KTable (RocksDB) | 5-min window aggregations |
| **Fraud Decisions** | Kafka Topics | Analysis results and routing |

### Data Flow

```
Raw Transaction → Velocity Aggregation → Customer Enrichment → AI Analysis → Decision
```

---

## 2. Transaction Schema

### Schema Definition

```python
@dataclass
class Transaction:
    transaction_id: str       # Unique identifier (e.g., "TXN_001")
    timestamp: str            # ISO format (e.g., "2025-12-21T23:00:15")
    customer_id: str          # Customer identifier (e.g., "CUST_001")
    amount: float             # Transaction amount in INR
    currency: str             # Currency code (e.g., "INR")
    merchant_name: str        # Merchant name (e.g., "Amazon India")
    merchant_category: str    # Category (e.g., "E-commerce", "Food")
    location: str             # Transaction location (e.g., "Mumbai, Maharashtra")
    payment_method: str       # Payment type (e.g., "Credit Card", "UPI")
```

### Sample Data

| Field | Example Values |
|-------|----------------|
| `transaction_id` | `NORMAL_001`, `VELOCITY_012`, `GAN_R5_003` |
| `timestamp` | `2025-12-21T23:00:15.102998` |
| `customer_id` | `CUST_NORMAL_001`, `CUST_VELOCITY_001` |
| `amount` | `10.0`, `500.0`, `2500.0`, `10000.0` |
| `currency` | `INR` |
| `merchant_name` | `Local Grocery Store`, `Amazon India`, `Premium Electronics Store` |
| `merchant_category` | `Groceries`, `E-commerce`, `Electronics`, `Luxury`, `Food & Beverage` |
| `location` | `Mumbai, Maharashtra`, `Delhi, NCR`, `Bangalore, Karnataka` |
| `payment_method` | `Debit Card`, `Credit Card`, `UPI` |

### Amount Distribution (Demo Scenarios)

| Scenario | Amount Range | Pattern |
|----------|--------------|---------|
| Normal | ₹500 | Single legitimate purchase |
| Card Testing | ₹10 → ₹25 → ₹50 → ₹100 → ₹200 → ₹500 | Progressive testing |
| Final Fraud | ₹2,500 | Large amount after testing |
| Amount Spike | ₹150 → ₹10,000 | Sudden 66x increase |
| GAN Attack | ₹500 - ₹5,000 | Random progressive |

---

## 3. Customer Profile Schema

### Schema Definition

```python
@dataclass
class CustomerProfile:
    customer_id: str                    # Unique customer ID
    average_transaction_amount: float   # Baseline average (INR)
    daily_spending_limit: float         # Daily limit (INR)
    transaction_categories: list        # Typical spending categories
    primary_location: str               # Home location
    risk_level: str                     # LOW, MEDIUM, HIGH
```

### Customer Profiles in System

| Customer ID | Avg Amount | Daily Limit | Categories | Location | Risk |
|-------------|------------|-------------|------------|----------|------|
| `CUST_NORMAL_001` | ₹500 | ₹10,000 | Groceries, Supermarket, Food | Mumbai | LOW |
| `CUST_VELOCITY_001` | ₹200 | ₹5,000 | Retail, Online | Delhi | MEDIUM |
| `CUST_SPIKE_001` | ₹150 | ₹8,000 | Groceries, Utilities | Bangalore | LOW |
| `CUST_GAN_001` | ₹1,000 | ₹20,000 | E-commerce, Electronics, Fashion | Mumbai | MEDIUM |

### Risk Level Distribution

```
Risk Levels:
├── LOW:    50% (2 customers)
├── MEDIUM: 50% (2 customers)
└── HIGH:   0%  (0 customers)
```

---

## 4. Velocity Context Schema

### Schema Definition

```python
class VelocityContext:
    customer_id: str              # Customer identifier
    transaction_count: int        # Transactions in window
    total_amount: float           # Sum of amounts in window
    avg_amount: float             # Average in window
    unique_locations: int         # Distinct locations
    unique_merchants: int         # Distinct merchants
    time_span_minutes: float      # Window duration
    velocity_score: float         # Transactions per minute
    rapid_fire_detected: bool     # Threshold exceeded
    window_start: str             # Window start time
    window_end: str               # Window end time (start + 5min)
```

### Sample Velocity Data (from KTable)

| Customer | Txn Count | Total Amount | Merchants | Velocity | Rapid Fire |
|----------|-----------|--------------|-----------|----------|------------|
| `CUST_VELOCITY_001` | 13 | ₹4,270 | 13 | 6.55/min | ✅ YES |
| `CUST_NORMAL_001` | 1 | ₹500 | 1 | 0.2/min | ❌ NO |

### Window Configuration

```python
VELOCITY_WINDOW_SIZE = 5  # minutes (tumbling window)
```

---

## 5. Fraud Decision Schema

### Schema Definition

```python
@dataclass
class FraudDecision:
    transaction_id: str           # Transaction analyzed
    final_score: float            # 0-100 risk score
    decision: str                 # APPROVED, REVIEW, FRAUD DETECTED
    risk_analyst_score: float     # RiskAssessor agent score
    pattern_detective_score: float # PatternDetector agent score
    decision_maker_reasoning: str # Explanation of decision
    agent_discussion: list        # All agent analyses
    timestamp: str                # Decision timestamp
```

### Decision Thresholds

| Risk Score | Decision | Routing Topic |
|------------|----------|---------------|
| 0-40% | ✅ APPROVED | `approved-transactions` |
| 40-80% | ⚠️ REVIEW | `human-review` |
| 80-100% | 🚨 FRAUD DETECTED | `fraud-alerts` |

---

## 6. Demo Scenarios Data

### Scenario 1: Normal Transaction

```json
{
  "transaction_id": "NORMAL_001",
  "customer_id": "CUST_NORMAL_001",
  "amount": 500.0,
  "merchant_name": "Local Grocery Store",
  "merchant_category": "Groceries",
  "location": "Mumbai, Maharashtra",
  "payment_method": "Debit Card"
}
```

**Expected Result:** ✅ APPROVED (Risk: ~13%)

### Scenario 2: High Velocity Attack (Card Testing)

12 rapid transactions followed by fraud attempt:

| # | Amount | Merchant | Timing |
|---|--------|----------|--------|
| 1 | ₹10 | Coffee Shop | +0s |
| 2 | ₹10 | Convenience Store | +10s |
| 3 | ₹25 | Gas Station | +20s |
| 4 | ₹25 | Fast Food | +30s |
| 5 | ₹50 | Pharmacy | +40s |
| 6 | ₹50 | Bookstore | +50s |
| 7 | ₹100 | Clothing Store | +60s |
| 8 | ₹100 | Electronics Shop | +70s |
| 9 | ₹200 | Department Store | +80s |
| 10 | ₹200 | Supermarket | +90s |
| 11 | ₹500 | Jewelry Store | +100s |
| 12 | ₹500 | Watch Shop | +110s |
| **13** | **₹2,500** | **Premium Electronics** | **+120s** |

**Pattern:** Progressive amounts (₹10 → ₹2,500)
**Expected Result:** 🚨 FRAUD DETECTED (Risk: ~97%)

### Scenario 3: Unusual Amount Spike

3 normal transactions followed by a spike:

| # | Amount | Type |
|---|--------|------|
| 1-3 | ₹150 each | Normal baseline |
| 4 | ₹10,000 | 66x spike! |

**Expected Result:** ⚠️ REVIEW (Risk: ~60-70%)

### Scenario 4: GAN Adversarial Attack

Random progressive amounts generated by AI:

| Round | Transactions | Amounts |
|-------|--------------|---------|
| 1 | 3-8 | ₹500 → ₹750 → ₹1,125 → ... |
| 2 | 3-8 | Learned from Round 1 failures |
| N | 3-8 | Continuously adapting |

---

## 7. EDA: Statistical Summary

### Transaction Amounts

```
📊 Amount Statistics:
├── Minimum:     ₹10 (card testing)
├── Maximum:     ₹10,000 (spike attack)
├── Normal Avg:  ₹150 - ₹1,000
├── Fraud Avg:   ₹2,500 - ₹10,000
└── Median:      ~₹200
```

### Velocity Statistics

```
📈 Velocity Statistics (5-min window):
├── Normal:      1-2 txns (0.2-0.4/min)
├── Suspicious:  5-10 txns (1-2/min)
├── Rapid-fire:  >15 txns (>3/min)
└── Card Testing: 10-15 txns, >5 merchants
```

### Location Distribution

```
📍 Locations:
├── Mumbai, Maharashtra:    40%
├── Delhi, NCR:             25%
├── Bangalore, Karnataka:   20%
├── Chennai, Tamil Nadu:    15%
└── Other:                  0%
```

### Merchant Categories

```
🏪 Categories:
├── E-commerce:       20%
├── Groceries:        20%
├── Electronics:      15%
├── Food & Beverage:  15%
├── Retail:           10%
├── Fashion:          10%
└── Luxury:           10%
```

---

## 8. EDA: Fraud Patterns

### Pattern 1: Card Testing (Velocity Attack)

**Characteristics:**
- 10+ transactions in 5 minutes
- Multiple unique merchants (>5)
- Progressive amounts (small → large)
- Same location
- Credit card payment method

**Detection Signals:**
```python
is_card_testing = (
    transaction_count > 10 and
    unique_merchants > 5 and
    velocity_score > 2.0
)
```

### Pattern 2: Amount Spike

**Characteristics:**
- Single large transaction
- 5x+ deviation from customer average
- May be legitimate (requires review)

**Detection Signals:**
```python
is_amount_spike = (
    amount > customer_avg * 5 or
    amount > daily_limit
)
```

### Pattern 3: Geographic Impossibility

**Characteristics:**
- Transaction from different city than primary
- Rapid location changes (location hopping)

**Detection Signals:**
```python
is_location_anomaly = (
    location != primary_location or
    unique_locations > 3  # in 5-min window
)
```

### Pattern 4: Temporal Anomaly

**Characteristics:**
- Unusual timing (late night, weekends)
- Scripted intervals (exactly 10s apart)

**Detection Signals:**
```python
is_temporal_anomaly = (
    velocity_score > 3.0 or  # Too regular
    time_span < expected_human_speed
)
```

---

## 9. Detection Thresholds

### Velocity Thresholds

| Metric | Normal | Warning | Alert |
|--------|--------|---------|-------|
| Transactions (5 min) | 1-5 | 5-10 | >10 |
| Velocity Score | <1.0 | 1.0-3.0 | >3.0 |
| Unique Merchants | 1-3 | 3-5 | >5 |
| Unique Locations | 1 | 2-3 | >3 |

### Amount Thresholds

| Metric | Normal | Warning | Alert |
|--------|--------|---------|-------|
| Deviation from Avg | <100% | 100-500% | >500% |
| vs Daily Limit | <50% | 50-100% | >100% |

### Streaming Bonus Points

| Condition | Points Added |
|-----------|--------------|
| Rapid-fire (>15 txns) | +20 |
| High velocity (>10 txns) | +10 |
| Location hopping (>3 locations) | +10 |
| Merchant hopping (>5 merchants) | +10 |
| Amount spike (>500% deviation) | +20 |
| Progressive testing pattern | +10 |
| Exceeds daily limit | +15 |
| High-risk customer | +10 |

---

## 📊 Data Quality Notes

1. **Synthetic Data:** All data is generated for demonstration; no real customer data
2. **Indian Context:** Amounts in INR, locations in India
3. **Timestamp Precision:** Millisecond precision for velocity calculations
4. **Missing Data:** No missing values in synthetic data
5. **Data Types:** All fields are properly typed (string, float, list)

---

## 🔗 Data Files

| File | Description |
|------|-------------|
| `ktable_state/velocity_ktable/` | RocksDB: Velocity aggregations |
| `ktable_state/customer_profiles_ktable/` | RocksDB: Customer profiles |
| `brain/memory/analyst_feedback.json` | Historical fraud decisions |

---

## 📈 How to Generate More Data

```python
# Run the demo multiple times to generate data:
python fraud_demo.py

# View the accumulated data:
python view_ktable.py
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-21
