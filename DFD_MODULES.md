# 📊 Data Flow Diagrams (DFD) & Module Description

This document provides level-wise Data Flow Diagrams and detailed module descriptions for the Agentic Fraud Detection System.

---

## 📋 Table of Contents

1. [DFD Level 0 (Context Diagram)](#1-dfd-level-0-context-diagram)
2. [DFD Level 1 (Main Processes)](#2-dfd-level-1-main-processes)
3. [DFD Level 2 (Detailed Processes)](#3-dfd-level-2-detailed-processes)
4. [Module Descriptions](#4-module-descriptions)
5. [Data Dictionary](#5-data-dictionary)

---

## 1. DFD Level 0 (Context Diagram)

The **Context Diagram** shows the system as a single process with external entities.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL ENTITIES                                  │
└──────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐                                        ┌─────────────┐
    │             │                                        │             │
    │  Customer   │                                        │  Analyst    │
    │  (Sender)   │                                        │  (Reviewer) │
    │             │                                        │             │
    └──────┬──────┘                                        └──────▲──────┘
           │                                                      │
           │ Transaction                              Review Queue │
           │ Request                                               │
           ▼                                                       │
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    ┌────────────────────────────────┐                        │
│                    │                                │                        │
│                    │   0.0  FRAUD DETECTION SYSTEM  │                        │
│                    │                                │                        │
│                    │   • Receives transactions      │                        │
│                    │   • Analyzes for fraud         │                        │
│                    │   • Routes decisions           │                        │
│                    │                                │                        │
│                    └────────────────────────────────┘                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
           │                                                       │
           │ Approved                                    Blocked   │
           │ Transaction                                Transaction│
           ▼                                                       ▼
    ┌─────────────┐                                        ┌─────────────┐
    │             │                                        │             │
    │  Payment    │                                        │  Alert      │
    │  Processor  │                                        │  System     │
    │             │                                        │             │
    └─────────────┘                                        └─────────────┘
```

### Level 0 Summary

| Entity | Data Flow | Direction |
|--------|-----------|-----------|
| Customer | Transaction Request | → System |
| Payment Processor | Approved Transaction | System → |
| Alert System | Blocked Transaction | System → |
| Analyst | Review Queue | System → |

---

## 2. DFD Level 1 (Main Processes)

Level 1 breaks down the system into **5 main processes**.

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                DFD LEVEL 1                                           │
└──────────────────────────────────────────────────────────────────────────────────────┘

                                    Transaction
    ┌─────────────┐                 Request              ┌─────────────────────┐
    │  Customer   │─────────────────────────────────────▶│  1.0 TRANSACTION    │
    └─────────────┘                                      │      INGESTION      │
                                                         │   (Kafka Producer)  │
                                                         └──────────┬──────────┘
                                                                    │
                                                         Raw Transaction (JSON)
                                                                    │
                                                                    ▼
┌─────────────────────┐                                  ┌─────────────────────┐
│                     │◀──── Velocity Context ──────────│  2.0 VELOCITY       │
│     D1: KTable      │                                  │      CALCULATION    │
│  (Velocity Store)   │────── Window Data ─────────────▶│   (5-min Window)    │
│                     │                                  └──────────┬──────────┘
└─────────────────────┘                                             │
                                                         Enriched Transaction
                                                                    │
┌─────────────────────┐                                             ▼
│                     │◀─── Customer Profile ───────────┌─────────────────────┐
│     D2: KTable      │                                  │  3.0 STREAMING      │
│  (Customer Store)   │────── Profile Lookup ──────────▶│     ENRICHMENT      │
│                     │                                  │    (leftJoins)      │
└─────────────────────┘                                  └──────────┬──────────┘
                                                                    │
                                                         Complete Context
                                                                    │
                                                                    ▼
                                                         ┌─────────────────────┐
                                                         │  4.0 AI AGENT       │
                                                         │      ANALYSIS       │
                                                         │   (5 Agents)        │
                                                         └──────────┬──────────┘
                                                                    │
                                                         Fraud Decision
                                                                    │
                                                                    ▼
                                                         ┌─────────────────────┐
                                                         │  5.0 INTELLIGENT    │
                                                         │      ROUTING        │
                                                         └──────────┬──────────┘
                                                                    │
                              ┌─────────────────────────────────────┼─────────────────────────────────────┐
                              │                                     │                                     │
                              ▼                                     ▼                                     ▼
                    ┌─────────────────┐                   ┌─────────────────┐                   ┌─────────────────┐
                    │  fraud-alerts   │                   │  human-review   │                   │    approved-    │
                    │     Topic       │                   │     Topic       │                   │  transactions   │
                    │   (>80% risk)   │                   │  (40-80% risk)  │                   │   (<40% risk)   │
                    └─────────────────┘                   └─────────────────┘                   └─────────────────┘
```

### Level 1 Process Summary

| Process | Name | Input | Output | Function |
|---------|------|-------|--------|----------|
| 1.0 | Transaction Ingestion | Transaction Request | Raw Transaction | Receive and publish to Kafka |
| 2.0 | Velocity Calculation | Raw Transaction | Velocity Context | Calculate 5-min window metrics |
| 3.0 | Streaming Enrichment | Transaction + Context | Enriched Transaction | Perform leftJoins |
| 4.0 | AI Agent Analysis | Enriched Transaction | Fraud Decision | 5-agent parallel analysis |
| 5.0 | Intelligent Routing | Fraud Decision | Routed Messages | Route to appropriate topic |

---

## 3. DFD Level 2 (Detailed Processes)

### 3.1 Process 2.0: Velocity Calculation (Expanded)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                         PROCESS 2.0: VELOCITY CALCULATION                            │
└──────────────────────────────────────────────────────────────────────────────────────┘

    Raw Transaction
          │
          ▼
┌─────────────────────┐
│  2.1 WINDOW         │
│      MANAGEMENT     │──────▶ Check if window expired
│                     │        (5-min tumbling)
└──────────┬──────────┘
           │
           │ Current Window
           ▼
┌─────────────────────┐        ┌─────────────────────┐
│  2.2 TRANSACTION    │        │                     │
│      AGGREGATION    │◀──────▶│   D1: Velocity      │
│                     │        │       KTable        │
└──────────┬──────────┘        │                     │
           │                   └─────────────────────┘
           │ Updated Metrics
           ▼
┌─────────────────────┐
│  2.3 VELOCITY       │
│      SCORING        │──────▶ Calculate txn/min
│                     │
└──────────┬──────────┘
           │
           │ Velocity Score
           ▼
┌─────────────────────┐
│  2.4 RAPID-FIRE     │
│      DETECTION      │──────▶ Check thresholds
│                     │        (>15 txns OR >3/min)
└──────────┬──────────┘
           │
           ▼
    Velocity Context
```

### 3.2 Process 4.0: AI Agent Analysis (Expanded)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                         PROCESS 4.0: AI AGENT ANALYSIS                               │
└──────────────────────────────────────────────────────────────────────────────────────┘

                              Enriched Transaction
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         4.1 PHASE 1:                │
                    │      PARALLEL ANALYSIS              │
                    └─────────────────────────────────────┘
                                      │
          ┌───────────┬───────────┬───┴───┬───────────┬───────────┐
          │           │           │       │           │           │
          ▼           ▼           ▼       ▼           ▼           │
    ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
    │  4.1.1    │ │  4.1.2    │ │  4.1.3    │ │  4.1.4    │ │  4.1.5    │
    │ Behavior  │ │ Pattern   │ │Geographic │ │   Risk    │ │ Temporal  │
    │ Analyst   │ │ Detector  │ │ Analyst   │ │ Assessor  │ │ Analyst   │
    │ (25%)     │ │ (25%)     │ │ (20%)     │ │ (15%)     │ │ (15%)     │
    └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
          │           │           │       │           │           │
          │           │           │       │           │           │
          └───────────┴───────────┴───┬───┴───────────┴───────────┘
                                      │
                              Agent Insights (5)
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │         4.2 COLLABORATION           │──▶ If variance > 40
                    │      PHASE (Talking Stage)          │    or velocity > 5
                    └─────────────────────────────────────┘
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          │                                                       │
          ▼                                                       ▼
┌─────────────────────┐                             ┌─────────────────────┐
│ 4.2.1 VELOCITY      │                             │ 4.2.2 PROFILE       │
│    COLLABORATION    │                             │    COLLABORATION    │
│ Pattern + Temporal  │                             │ Behavior + Risk     │
└──────────┬──────────┘                             └──────────┬──────────┘
           │                                                   │
           └───────────────────────┬───────────────────────────┘
                                   │
                           Collaboration Insights
                                   │
                                   ▼
                    ┌─────────────────────────────────────┐
                    │         4.3 WEIGHTED               │
                    │      CONSENSUS SCORING             │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │         4.4 STREAMING              │──▶ Apply velocity
                    │      INTELLIGENCE BONUS            │    and profile bonuses
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                                Fraud Decision
```

### 3.3 Process 5.0: Intelligent Routing (Expanded)

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                         PROCESS 5.0: INTELLIGENT ROUTING                             │
└──────────────────────────────────────────────────────────────────────────────────────┘

                                Fraud Decision
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   5.1 CONFIDENCE-BASED             │
                    │       EVALUATION                   │
                    └──────────────────┬──────────────────┘
                                       │
                         ┌─────────────┴─────────────┐
                         │                           │
               ┌─────────▼─────────┐       ┌─────────▼─────────┐
               │  5.2 HIGH RISK    │       │  5.3 LOW/MEDIUM   │
               │  ROUTING          │       │  ROUTING          │
               │  (score > 80%)    │       │  (score < 80%)    │
               └─────────┬─────────┘       └─────────┬─────────┘
                         │                           │
                         │              ┌────────────┴────────────┐
                         │              │                         │
                         ▼              ▼                         ▼
               ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
               │ 5.2.1           │ │ 5.3.1           │ │ 5.3.2           │
               │ FRAUD ALERT     │ │ HUMAN REVIEW    │ │ AUTO APPROVE    │
               │ (>80% + >90%    │ │ (40-80% OR      │ │ (<40% risk)     │
               │  confidence)    │ │  uncertain)     │ │                 │
               └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
                        │                   │                   │
                        ▼                   ▼                   ▼
               ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
               │  fraud-alerts   │ │  human-review   │ │    approved-    │
               │     Topic       │ │     Topic       │ │  transactions   │
               └─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 4. Module Descriptions

### 4.1 Transaction Ingestion Module

| Property | Details |
|----------|---------|
| **File** | `fraud_demo.py`, `producer.py` |
| **Class** | `InteractiveFraudDemo` |
| **Function** | Receives transaction requests and publishes to Kafka |

```python
# Key Methods:
def publish_transaction(self, transaction):
    """Publish transaction to Kafka 'transactions' topic"""
    self.producer.send('transactions', key=tx_id, value=tx_data)
```

**Data Flow:**
```
User Input → Transaction Object → JSON Serialization → Kafka Producer → transactions topic
```

---

### 4.2 Velocity Calculation Module

| Property | Details |
|----------|---------|
| **File** | `velocity_ktable.py` |
| **Classes** | `VelocityWindow`, `VelocityKTable` |
| **Function** | Calculate 5-min tumbling window aggregations |

```python
# Key Classes:
class VelocityWindow:
    """5-minute tumbling window for velocity calculation"""
    window_size = 5  # minutes
    
    def add_transaction(self, tx):
        """Add transaction and recalculate metrics"""
        
    def get_metrics(self):
        """Return velocity_score, transaction_count, etc."""

class VelocityKTable:
    """RocksDB-backed state store for velocity context"""
    
    def update(self, customer_id, transaction):
        """Update customer's velocity stats"""
        
    def get(self, customer_id):
        """Retrieve current velocity context"""
```

**Data Flow:**
```
Transaction → Window Check → Aggregate Metrics → Store in RocksDB → Return Velocity Context
```

**Output Structure:**
```json
{
  "transaction_count": 12,
  "total_amount": 4270.0,
  "avg_amount": 355.83,
  "unique_locations": 1,
  "unique_merchants": 12,
  "velocity_score": 6.55,
  "rapid_fire_detected": true
}
```

---

### 4.3 Streaming Enrichment Module

| Property | Details |
|----------|---------|
| **File** | `velocity_ktable.py` |
| **Class** | `StreamingContextWithKTable` |
| **Function** | Perform leftJoins to enrich transactions |

```python
class StreamingContextWithKTable:
    """Integrates velocity and profile KTables"""
    
    def get_streaming_context(self, customer_id, transaction):
        """
        Perform leftJoins:
        1. Transaction + Velocity Context
        2. Transaction + Customer Profile
        Returns enriched context with anomaly detection
        """
```

**Data Flow:**
```
Transaction → Velocity KTable (leftJoin) → Customer Profile KTable (leftJoin) → Anomaly Detection → Enriched Context
```

**Output Structure:**
```json
{
  "velocity": { /* velocity metrics */ },
  "profile": { /* customer baseline */ },
  "baseline": { /* avg_amount, primary_location, etc. */ },
  "anomalies": {
    "velocity_alert": true,
    "rapid_fire_detected": true,
    "amount_deviation_pct": 1150.0
  },
  "risk_indicators": {
    "high_velocity": true,
    "merchant_hopping": true
  }
}
```

---

### 4.4 AI Agent Analysis Module

| Property | Details |
|----------|---------|
| **File** | `production_coordinator.py`, `agents/*.py` |
| **Class** | `ProductionAgentCoordinator` |
| **Function** | Orchestrate 5 AI agents for fraud analysis |

#### 4.4.1 Agent Classes

| Agent | File | Weight | Specialization |
|-------|------|--------|----------------|
| **BehaviorAnalyst** | `agents/behavior_analyst.py` | 25% | Customer behavior patterns |
| **PatternDetector** | `agents/pattern_detector_v2.py` | 25% | Fraud patterns (card testing, etc.) |
| **GeographicAnalyst** | `agents/geographic_analyst.py` | 20% | Location anomalies |
| **RiskAssessor** | `agents/risk_assessor.py` | 15% | Profile-based risk |
| **TemporalAnalyst** | `agents/temporal_analyst.py` | 15% | Time-based anomalies |

```python
class ProductionAgentCoordinator:
    """Orchestrates 5 specialized agents"""
    
    AGENT_WEIGHTS = {
        'BehaviorAnalyst': 0.25,
        'PatternDetector': 0.25,
        'GeographicAnalyst': 0.20,
        'RiskAssessor': 0.15,
        'TemporalAnalyst': 0.15
    }
    
    def analyze_transaction(self, transaction):
        """
        Phase 1: Parallel 5-agent analysis
        Phase 2: Agent collaboration (if needed)
        Phase 3: Streaming intelligence bonus
        Returns: (FraudDecision, confidence)
        """
```

**Data Flow:**
```
Enriched Transaction 
    → Phase 1: 5 Parallel Agents
    → Phase 2: Collaboration (if variance > 40)
    → Phase 3: Weighted Consensus
    → Phase 4: Streaming Bonus
    → Final Decision
```

---

### 4.5 Intelligent Routing Module

| Property | Details |
|----------|---------|
| **File** | `intelligent_router.py` |
| **Class** | `IntelligentRouter` |
| **Function** | Route decisions to appropriate Kafka topics |

```python
class IntelligentRouter:
    """Routes fraud decisions based on confidence"""
    
    def route_decision(self, decision_dict, confidence):
        """
        Routing Rules:
        - fraud-alerts:  score > 80% AND confidence > 90%
        - human-review:  score 40-80% OR uncertain
        - approved:      score < 40%
        """
```

**Routing Logic:**
```python
if is_fraudulent and confidence > 90:
    return 'fraud-alerts'       # Auto-block
elif is_fraudulent or is_uncertain:
    return 'human-review'       # Manual review
else:
    return 'approved-transactions'  # Auto-approve
```

---

### 4.6 Storage Modules (KTables)

| KTable | File | Storage | Purpose |
|--------|------|---------|---------|
| **Velocity KTable** | `velocity_ktable.py` | RocksDB | 5-min window aggregations |
| **Customer Profile KTable** | `velocity_ktable.py` | RocksDB | Customer baselines |

```
📂 ktable_state/
   ├── velocity_ktable/           # Transaction velocity per customer
   └── customer_profiles_ktable/  # Customer baseline profiles
```

---

### 4.7 Visualization Module

| Property | Details |
|----------|---------|
| **File** | `gan_dashboard.py` |
| **Class** | Flask App |
| **Function** | Real-time GAN training visualization |

```python
# Flask routes:
@app.route('/')           # Dashboard home
@app.route('/api/update') # Receive training updates
@app.route('/api/reset')  # Reset training session
```

---

## 5. Data Dictionary

### 5.1 Transaction Data

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `transaction_id` | String | Unique identifier | `"TXN_001"` |
| `timestamp` | String (ISO) | Transaction time | `"2025-12-21T23:00:15"` |
| `customer_id` | String | Customer identifier | `"CUST_001"` |
| `amount` | Float | Amount in INR | `2500.0` |
| `currency` | String | Currency code | `"INR"` |
| `merchant_name` | String | Merchant name | `"Amazon India"` |
| `merchant_category` | String | Category | `"E-commerce"` |
| `location` | String | Transaction location | `"Mumbai, Maharashtra"` |
| `payment_method` | String | Payment type | `"Credit Card"` |

### 5.2 Velocity Context Data

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `transaction_count` | Integer | Transactions in 5-min window | `12` |
| `total_amount` | Float | Sum of amounts | `4270.0` |
| `velocity_score` | Float | Transactions per minute | `6.55` |
| `rapid_fire_detected` | Boolean | Threshold exceeded | `true` |
| `unique_merchants` | Integer | Distinct merchants | `12` |
| `unique_locations` | Integer | Distinct locations | `1` |

### 5.3 Fraud Decision Data

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `final_score` | Float | Risk score (0-100) | `97.1` |
| `decision` | String | Decision label | `"FRAUD DETECTED"` |
| `confidence` | Float | Decision confidence | `86.0` |
| `agent_discussion` | List | All agent analyses | `[{...}]` |

---

## 📊 Summary Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        COMPLETE SYSTEM DATA FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│   Customer ──▶ [1.0 Ingestion] ──▶ transactions topic                               │
│                                            │                                        │
│                                            ▼                                        │
│                                   [2.0 Velocity Calc] ◀──▶ 📦 Velocity KTable       │
│                                            │                                        │
│                                            ▼                                        │
│                                   [3.0 Enrichment] ◀──────▶ 📦 Profile KTable       │
│                                            │                                        │
│                                            ▼                                        │
│                                   [4.0 AI Analysis]                                 │
│                              ┌────────────────────────────┐                         │
│                              │ 🔴 BehaviorAnalyst   (25%) │                         │
│                              │ 🟢 PatternDetector   (25%) │                         │
│                              │ 🔵 GeographicAnalyst (20%) │                         │
│                              │ 🟡 RiskAssessor      (15%) │                         │
│                              │ 🟣 TemporalAnalyst   (15%) │                         │
│                              └────────────────────────────┘                         │
│                                            │                                        │
│                                            ▼                                        │
│                                   [5.0 Routing]                                     │
│                                            │                                        │
│                    ┌───────────────────────┼───────────────────────┐                │
│                    ▼                       ▼                       ▼                │
│            🚨 fraud-alerts         ⚠️ human-review         ✅ approved              │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-21
