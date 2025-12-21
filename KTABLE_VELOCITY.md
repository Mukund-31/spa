# KTable & Velocity Windows Implementation

This document explains the Kafka Streams architecture with **KTable** and **velocity windows** for detecting rapid-fire attacks.

## Architecture Overview (Matching the Diagram)

```
┌─────────────────┐     ┌─────────────────────┐
│  transactions   │     │  customerProfiles   │
│    (KStream)    │     │     (KStore)        │
└────────┬────────┘     └──────────┬──────────┘
         │                         │
         ▼                         │
┌─────────────────┐                │
│  VELOCITY CALC  │                │
│  (5-min window) │                │
│    KStream      │                │
└────────┬────────┘                │
         │                         │
         ▼                         │
┌─────────────────┐                │
│ Velocity Context│                │
│    (KTable)     │◄───────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         STREAMING ENRICHMENT LAYER          │
│  ┌─────────────────────────────────────┐   │
│  │ Transaction + (leftJoin)            │   │
│  │ Velocity Context + (leftJoin)       │   │
│  │ Customer Profile                    │   │
│  └─────────────────────────────────────┘   │
│                    ↓                        │
│         EnrichedTransaction (KStream)       │
│      {txn, customerProfile, velocity}       │
└─────────────────────────────────────────────┘
```

## Components Implemented

### 1. Velocity Window (5-minute Tumbling)

**File:** `velocity_ktable.py` - `VelocityWindow` class

```python
from datetime import timedelta

# 5-minute tumbling window for velocity calculation
VELOCITY_WINDOW = 5  # minutes

# Rapid-fire detection thresholds
RAPID_FIRE_THRESHOLDS = {
    'transaction_count': 15,    # >15 txns in 5 min = rapid-fire
    'velocity_score': 3.0,      # >3 txns per minute = rapid-fire
    'card_testing_pattern': 10, # >10 txns with >5 merchants = card testing
}
```

**What it does:**
- Tracks all transactions within a 5-minute sliding window
- Calculates `velocity_score` (transactions per minute)
- Detects `rapid_fire_detected` when thresholds exceeded
- "Tumbles" the window - clears old data when window expires

### 2. KTable: Velocity Context

**File:** `velocity_ktable.py` - `VelocityKTable` class

```python
class VelocityKTable:
    """
    KTable implementation backed by RocksDB state store
    Persists velocity context across restarts
    """
    
    def __init__(self, state_dir: str = './ktable_state'):
        # RocksDB provides persistent state (like Kafka Streams)
        self.db = rocksdb.DB(os.path.join(state_dir, 'velocity_ktable.db'), opts)
```

**What it stores:**
- `transaction_count`: Number of transactions in window
- `total_amount`: Sum of all transaction amounts
- `unique_locations`: List of distinct locations (for location hopping)
- `unique_merchants`: List of distinct merchants (for card testing)
- `velocity_score`: Transactions per minute
- `rapid_fire_detected`: Boolean flag

### 3. KTable: Customer Profiles

**File:** `velocity_ktable.py` - `CustomerProfileKTable` class

```python
class CustomerProfileKTable:
    """
    KTable for customer profiles (from customerProfiles topic)
    """
    
    # Stores:
    # - average_transaction_amount
    # - daily_spending_limit
    # - transaction_categories
    # - primary_location
    # - risk_level
```

### 4. Stream Enrichment (leftJoin)

**File:** `velocity_ktable.py` - `StreamingContextWithKTable.get_streaming_context()`

```python
def get_streaming_context(self, customer_id: str, current_transaction: Dict) -> Dict:
    """
    Performs the stream enrichment (leftJoins) from the architecture diagram:
    1. Transaction + Velocity Context (leftJoin)
    2. Transaction + Customer Profile (leftJoin)
    """
    velocity = self.velocity_ktable.get(customer_id)  # leftJoin
    profile = self.profile_ktable.get(customer_id)    # leftJoin
    
    return {
        'velocity': velocity,
        'profile': profile,
        'anomalies': {...},
        'risk_indicators': {...},
    }
```

## Faust Kafka Streams (Optional)

**File:** `kafka_streams.py`

For true distributed Kafka Streams processing, we provide a Faust-based implementation:

```python
import faust
from faust import windows

# 5-minute tumbling window
VELOCITY_WINDOW = windows.TumblingWindow(size=timedelta(minutes=5))

# Velocity table with windowed aggregation
velocity_table = app.Table(
    'velocity-context-table',
    default=lambda: {...},
).tumbling(VELOCITY_WINDOW, expires=timedelta(minutes=15))
```

### Running Faust Worker

```bash
# Start the Kafka Streams processor
python kafka_streams.py worker -l info
```

## Detection Thresholds

| Pattern | Threshold | Bonus Points |
|---------|-----------|--------------|
| **Rapid-fire attack** | >15 txns in 5 min | +20 |
| **High velocity** | >10 txns in 5 min | +10 |
| **Velocity score** | >3 txns/min | rapid_fire=True |
| **Location hopping** | >3 unique locations | +10 |
| **Merchant hopping** | >5 unique merchants | +10 |
| **Card testing** | >10 txns + >5 merchants | +15 |

## Example Detection Flow

```
1. Transaction arrives: TXN_001 from CUST_001

2. Velocity KTable lookup:
   └─ customer_id: CUST_001
   └─ current_window: 2025-12-21 22:30:00 → 22:35:00
   └─ transaction_count: 12
   └─ velocity_score: 2.4 txn/min
   └─ unique_merchants: 8

3. Customer Profile lookup:
   └─ average_transaction_amount: ₹500
   └─ primary_location: "Mumbai"
   └─ risk_level: "LOW"

4. Enrichment Result:
   {
     "velocity": {
       "transaction_count": 13,     # Updated
       "velocity_score": 2.6,       # Updated
       "rapid_fire_detected": false
     },
     "baseline": {
       "avg_amount": 500,
       "primary_location": "Mumbai"
     },
     "risk_indicators": {
       "high_velocity": true,       # >10 txns
       "merchant_hopping": true     # >5 merchants
     }
   }

5. Streaming Bonus Applied:
   └─ Base Score: 55%
   └─ High Velocity: +10 points
   └─ Merchant Hopping: +10 points
   └─ Final Score: 75% → REVIEW
```

## Usage

### In Production Coordinator

```python
from velocity_ktable import StreamingContextWithKTable

# Initialize KTable-backed context
context_store = StreamingContextWithKTable(state_dir='./ktable_state')

# Add customer profile (from customerProfiles topic)
context_store.add_customer_profile({
    'customer_id': 'CUST_001',
    'average_transaction_amount': 500.0,
    'primary_location': 'Mumbai',
    'risk_level': 'LOW'
})

# Process transaction (updates velocity KTable)
velocity = context_store.add_transaction(transaction_dict)

# Get enriched context for analysis
streaming_context = context_store.get_streaming_context(
    customer_id='CUST_001',
    current_transaction=transaction_dict
)

# Check for rapid-fire
if streaming_context['velocity']['rapid_fire_detected']:
    print("🚨 RAPID-FIRE ATTACK DETECTED!")
```

## State Store Location

```
./ktable_state/
├── velocity_ktable.db/      # RocksDB database for velocity
│   ├── CURRENT
│   ├── MANIFEST-*
│   ├── OPTIONS-*
│   └── *.sst              # SST files (sorted string tables)
└── customer_profiles_ktable.db/  # RocksDB for profiles
```

## Summary

| Component | Implementation | State Store |
|-----------|----------------|-------------|
| Velocity Window | 5-min tumbling | RocksDB |
| Velocity KTable | `VelocityKTable` class | RocksDB |
| Customer Profile KTable | `CustomerProfileKTable` class | RocksDB |
| Stream Enrichment | `get_streaming_context()` | N/A (joins) |
| Rapid-fire Detection | Threshold-based | Real-time |

The implementation now **matches the architecture diagram** with proper KTable and velocity windows for detecting rapid-fire attacks!
