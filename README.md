# 🚨 Agentic Fraud Detection System

A real-time fraud detection system using **5 AI Agents**, **Kafka Streams**, **KTable**, and **Velocity Windows** for detecting rapid-fire attacks.

![Architecture](https://img.shields.io/badge/Architecture-Kafka%20Streams-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![AI](https://img.shields.io/badge/AI-Gemini%20Flash-orange)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Full Setup Guide](#-full-setup-guide)
- [Running the Demo](#-running-the-demo)
- [Viewing KTable Data](#-viewing-ktable-data)
- [Understanding the System](#-understanding-the-system)
- [Commands Reference](#-commands-reference)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **5 AI Agents** | BehaviorAnalyst, PatternDetector, GeographicAnalyst, RiskAssessor, TemporalAnalyst |
| **KTable** | RocksDB-backed state store for customer profiles and velocity tracking |
| **Velocity Windows** | 5-minute tumbling windows for rapid-fire attack detection |
| **Streaming Enrichment** | leftJoin operations to enrich transactions with customer context |
| **Intelligent Routing** | Auto-route to fraud-alerts, human-review, or approved-transactions |
| **GAN Mode** | AI vs AI adversarial training for improved detection |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KAFKA INPUT TOPICS                           │
├─────────────────┬───────────────────────────────────────────────┤
│  transactions   │              customerProfiles                 │
│   (KStream)     │                 (KStore)                      │
└────────┬────────┴──────────────────────┬────────────────────────┘
         │                               │
         ▼                               │
┌─────────────────┐                      │
│  VELOCITY CALC  │                      │
│  5-min window   │                      │
│   (KStream)     │                      │
└────────┬────────┘                      │
         │                               │
         ▼                               │
┌─────────────────┐                      │
│Velocity Context │◄─────────────────────┘
│   (KTable)      │
│  RocksDB-backed │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              STREAMING ENRICHMENT LAYER                         │
│  Transaction + (leftJoin) Velocity + (leftJoin) CustomerProfile │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              5 AI AGENTS (Parallel Analysis)                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│  Behavior   │   Pattern   │ Geographic  │    Risk     │Temporal │
│  Analyst    │  Detector   │  Analyst    │  Assessor   │ Analyst │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INTELLIGENT ROUTING                            │
├──────────────────┬──────────────────┬───────────────────────────┤
│   fraud-alerts   │   human-review   │   approved-transactions   │
│   (>80% risk)    │   (40-80% risk)  │      (<40% risk)          │
└──────────────────┴──────────────────┴───────────────────────────┘
```

---

## 🚀 Quick Start

```bash
# 1. Clone and enter directory
cd c:\Users\mukun\Desktop\spa

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment (Windows)
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Kafka (Docker required)
docker-compose up -d

# 6. Run the demo
python fraud_demo.py
```

---

## 📦 Full Setup Guide

### Prerequisites

- **Python 3.10+**
- **Docker Desktop** (for Kafka)
- **Gemini API Key** (for AI agents)

### Step 1: Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
venv\Scripts\activate

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually:
pip install kafka-python==2.0.2
pip install google-generativeai==0.3.2
pip install python-dotenv==1.0.0
pip install Faker==20.1.0
pip install colorama==0.4.6
pip install faust-streaming==0.10.19
pip install rocksdict
pip install flask==3.0.0
pip install requests==2.31.0
```

### Step 3: Configure API Key

Create a `.env` file:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
KAFKA_BOOTSTRAP_SERVERS=localhost:9093
```

### Step 4: Start Kafka

```bash
# Start Kafka, Zookeeper, and Kafka UI
docker-compose up -d

# Verify containers are running
docker ps

# Expected output:
# - zookeeper (port 2181)
# - kafka (ports 9092, 9093)
# - kafka-ui (port 8080)
```

### Step 5: Create Kafka Topics (Optional)

```bash
# Topics are auto-created, but you can create manually:
python kafka_admin.py
```

---

## 🎮 Running the Demo

### Main Demo (Interactive)

```bash
# Activate virtual environment first
venv\Scripts\activate

# Run the interactive demo
python fraud_demo.py
```

### Demo Scenarios

| Scenario | Description | Expected Result |
|----------|-------------|-----------------|
| **1. Normal Transaction** | ₹500 grocery purchase | ✅ APPROVED (low risk) |
| **2. High Velocity Attack** | 12 rapid transactions + ₹2,500 final | 🚨 FRAUD DETECTED |
| **3. Unusual Amount Spike** | ₹150 avg → ₹10,000 spike | ⚠️ REVIEW |
| **4. AI vs AI (GAN Mode)** | Adversarial training loop | Learning both sides |

### GAN Dashboard

```bash
# Start the GAN training dashboard (optional)
python gan_dashboard.py

# View at: http://localhost:5001
```

---

## 📊 Viewing KTable Data

### View All KTable Contents

```bash
python view_ktable.py
```

**Example Output:**
```
📊 KTABLE VIEWER
======================================================================

📈 VELOCITY KTABLE (velocity_ktable)
----------------------------------------------------------------------
🔑 Key: velocity:CUST_VELOCITY_001
   📊 Transactions in window: 13
   💰 Total amount: ₹4,270.00
   🏪 Unique merchants: 13
   ⏰ Window: 23:00:15 → 23:05:15

👤 CUSTOMER PROFILE KTABLE (customer_profiles_ktable)
----------------------------------------------------------------------
🔑 Key: profile:CUST_NORMAL_001
   💰 Avg Transaction: ₹500.00
   📍 Primary Location: Mumbai
   ⚠️  Risk Level: LOW
```

### KTable Storage Location

```
📂 ktable_state/
   ├── velocity_ktable/           # Velocity tracking data
   │   ├── CURRENT
   │   ├── MANIFEST-*
   │   └── *.sst
   └── customer_profiles_ktable/  # Customer profiles
       ├── CURRENT
       ├── MANIFEST-*
       └── *.sst
```

---

## 🧠 Understanding the System

### KTable vs Kafka Topic

| Kafka Topic | KTable |
|-------------|--------|
| Log of all transactions | Current state per customer |
| Append-only | Updated in-place |
| Used for history/replay | Used for fast lookups |
| Like a diary | Like a scoreboard |

### Velocity Window (5-min Tumbling)

```python
# Thresholds for rapid-fire detection:
rapid_fire_detected = (
    transaction_count > 15 or      # >15 txns in 5 min
    velocity_score > 3.0 or        # >3 txns per minute
    (txn_count > 10 and merchants > 5)  # Card testing
)
```

### Streaming Enrichment (leftJoin)

```
Transaction → leftJoin(Velocity) → leftJoin(CustomerProfile) → EnrichedTransaction
```

---

## 📝 Commands Reference

### Environment Commands

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate

# Install all dependencies
pip install -r requirements.txt
```

### Docker Commands

```bash
# Start Kafka stack
docker-compose up -d

# Stop Kafka stack
docker-compose down

# View logs
docker-compose logs -f kafka

# Check container status
docker ps
```

### Demo Commands

```bash
# Run interactive fraud demo
python fraud_demo.py

# View KTable contents
python view_ktable.py

# Start GAN dashboard
python gan_dashboard.py

# Run Kafka Streams worker (optional)
python kafka_streams.py worker -l info
```

### Admin Commands

```bash
# Create Kafka topics
python kafka_admin.py

# Test agents
python test_agents.py

# Test streaming context
python test_streaming_context.py

# Test production system
python test_production.py
```

---

## 📁 Project Structure

```
spa/
├── fraud_demo.py              # Main interactive demo
├── production_coordinator.py  # 5-agent orchestrator
├── velocity_ktable.py         # KTable implementation (RocksDB)
├── streaming_context.py       # Original streaming context
├── kafka_streams.py           # Faust Kafka Streams (optional)
├── view_ktable.py            # KTable viewer utility
├── intelligent_router.py     # Decision routing logic
├── gan_dashboard.py          # GAN training visualization
├── config.py                 # Configuration settings
├── models.py                 # Data models
├── knowledge_base.py         # Agent learning memory
│
├── agents/                   # AI Agent implementations
│   ├── base_agent.py
│   ├── behavior_analyst.py
│   ├── pattern_detector_v2.py
│   ├── geographic_analyst.py
│   ├── risk_assessor.py
│   └── temporal_analyst.py
│
├── ktable_state/             # RocksDB storage (auto-created)
│   ├── velocity_ktable/
│   └── customer_profiles_ktable/
│
├── docker-compose.yml        # Kafka Docker setup
├── requirements.txt          # Python dependencies
└── .env                      # API keys (create this)
```

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: kafka` | Run `pip install kafka-python` |
| `RocksDB not available` | Run `pip install rocksdict` |
| `Kafka connection refused` | Start Docker: `docker-compose up -d` |
| `GEMINI_API_KEY not found` | Create `.env` file with your API key |

### Verify Setup

```bash
# Check Python version
python --version  # Should be 3.10+

# Check Docker
docker ps  # Should show kafka, zookeeper, kafka-ui

# Test Kafka connection
python -c "from kafka import KafkaProducer; print('Kafka OK')"

# Test RocksDB
python -c "from rocksdict import Rdict; print('RocksDB OK')"
```

---

## 🔗 URLs

| Service | URL |
|---------|-----|
| **Kafka UI** | http://localhost:8080 |
| **GAN Dashboard** | http://localhost:5001 |

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🙏 Acknowledgments

- **Google Gemini** - AI Agent intelligence
- **Apache Kafka** - Stream processing
- **RocksDB** - State store
- **Faust** - Python Kafka Streams

---

**Made with ❤️ for fraud detection**
