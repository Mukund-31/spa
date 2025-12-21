# 📋 Component Functional Responsibilities

This document provides detailed tables of all components/files in the Agentic Fraud Detection System and their functional responsibilities.

---

## Table 1: Core Application Components

| Component / File | Functionality |
|------------------|---------------|
| `fraud_demo.py` | Main interactive demo application. Orchestrates 4 fraud scenarios, manages Kafka producer, and coordinates with the production system for real-time fraud analysis. |
| `production_coordinator.py` | Central orchestrator for 5 AI agents with weighted voting. Manages parallel agent analysis, collaboration phases, streaming intelligence bonuses, and final fraud decision generation. |
| `config.py` | Configuration management for Kafka bootstrap servers, topic names, Gemini API keys, and system-wide settings. |
| `models.py` | Data model definitions using Python dataclasses. Defines `Transaction`, `CustomerProfile`, `AgentAnalysis`, and `FraudDecision` schemas with JSON serialization. |
| `run.py` | Application entry point for running the fraud detection system in production mode with Kafka consumers and real-time processing. |

---

## Table 2: AI Agent Components

| Component / File | Functionality |
|------------------|---------------|
| `agents/base_agent.py` | Abstract base class for all AI agents. Provides common interface for Gemini API calls, response parsing, and error handling. |
| `agents/behavior_analyst.py` | Analyzes customer spending behavior patterns. Detects deviations from historical baselines and unusual behavioral indicators. Weight: **25%** |
| `agents/pattern_detector_v2.py` | Detects known fraud patterns including card testing, progressive amounts, merchant hopping, and rapid-fire attacks. Weight: **25%** |
| `agents/geographic_analyst.py` | Analyzes geographic anomalies. Detects location hopping, impossible travel, and transactions from unusual regions. Weight: **20%** |
| `agents/risk_assessor.py` | Profile-based risk evaluation. Assesses risk level based on customer history, transaction categories, and spending limits. Weight: **15%** |
| `agents/temporal_analyst.py` | Time-based anomaly detection. Identifies suspicious timing patterns, scripted intervals, and unusual transaction hours. Weight: **15%** |
| `agents/decision_maker.py` | Legacy decision aggregation agent. Combines individual agent scores into final weighted decision. |
| `agents/fraud_generator.py` | GAN adversarial agent. Generates synthetic fraud attempts to test and improve detection capabilities. |
| `agents/risk_analyst.py` | Legacy risk scoring agent. Provides baseline risk assessment for transactions. |
| `agents/pattern_detective.py` | Legacy pattern matching agent. Identifies basic fraud signatures and known attack vectors. |

---

## Table 3: Kafka Streaming Components

| Component / File | Functionality |
|------------------|---------------|
| `producer.py` | Kafka message producer. Publishes transactions and customer profiles to Kafka topics with JSON serialization. |
| `consumer.py` | Kafka message consumer. Subscribes to transaction topics and triggers fraud analysis pipeline. |
| `enhanced_consumer.py` | Advanced Kafka consumer with batch processing support and rate-limiting for AI API calls. |
| `kafka_admin.py` | Kafka administration utilities. Creates topics, manages partitions, and configures retention policies. |
| `kafka_streams.py` | Faust-based Kafka Streams implementation. Defines streaming topology, KTable joins, and windowed aggregations. |
| `intelligent_router.py` | Decision routing engine. Routes fraud decisions to appropriate Kafka topics based on risk score and confidence thresholds. |

---

## Table 4: State Management & KTable Components

| Component / File | Functionality |
|------------------|---------------|
| `velocity_ktable.py` | RocksDB-backed KTable implementation for velocity tracking. Manages 5-minute tumbling windows, calculates velocity metrics, and detects rapid-fire attacks. |
| `streaming_context.py` | In-memory streaming context store. Maintains customer transaction history, velocity windows, and anomaly indicators as fallback when RocksDB unavailable. |
| `view_ktable.py` | KTable inspection utility. Displays contents of velocity and customer profile KTables stored in RocksDB for debugging. |
| `knowledge_base.py` | Agent learning memory store. Persists fraud patterns, detection feedback, and agent learning history for continuous improvement. |

---

## Table 5: Coordinator & Orchestration Components

| Component / File | Functionality |
|------------------|---------------|
| `agent_coordinator.py` | Basic 3-agent coordinator. Manages Risk Analyst, Pattern Detective, and Decision Maker for simplified fraud analysis pipeline. |
| `enhanced_agent_coordinator.py` | Enhanced multi-agent coordinator with collaboration support. Implements agent discussion, consensus building, and knowledge sharing. |
| `production_coordinator.py` | Production-grade 5-agent coordinator with streaming intelligence. Implements weighted voting, phase-based analysis, and real-time velocity bonuses. |

---

## Table 6: Visualization & Dashboard Components

| Component / File | Functionality |
|------------------|---------------|
| `gan_dashboard.py` | Flask-based real-time dashboard for GAN training visualization. Displays adversarial attack rounds, detection rates, and fraudster evolution metrics. |

---

## Table 7: Infrastructure & Configuration Files

| Component / File | Functionality |
|------------------|---------------|
| `docker-compose.yml` | Docker orchestration for Kafka ecosystem. Configures Zookeeper, Kafka broker, and Kafka UI services with proper networking. |
| `requirements.txt` | Python dependency specifications. Lists all required packages including kafka-python, google-generativeai, faust-streaming, rocksdict, and flask. |
| `setup.bat` | Windows batch script for automated environment setup. Creates virtual environment and installs dependencies. |
| `.env` | Environment variables configuration. Stores GEMINI_API_KEY and KAFKA_BOOTSTRAP_SERVERS securely. |
| `.gitignore` | Git ignore patterns. Excludes virtual environment, cache files, and sensitive configuration from version control. |

---

## Table 8: Testing Components

| Component / File | Functionality |
|------------------|---------------|
| `test_agents.py` | Unit tests for individual AI agents. Validates agent response parsing, score calculation, and error handling. |
| `test_production.py` | Integration tests for production coordinator. Tests end-to-end fraud analysis pipeline with mock transactions. |
| `test_streaming_context.py` | Unit tests for streaming context store. Validates velocity window calculations, rapid-fire detection, and customer profiling. |

---

## Table 9: Helper & Utility Components

| Component / File | Functionality |
|------------------|---------------|
| `_fix_syntax.py` | Syntax fixing utility. Repairs malformed JSON responses from AI agents with regex-based corrections. |
| `_gan_helpers.py` | GAN training helper functions. Provides utilities for adversarial attack generation and dashboard updates. |

---

## Table 10: Data Storage Directories

| Directory | Functionality |
|-----------|---------------|
| `ktable_state/` | RocksDB database files for persistent KTable storage. Contains velocity and customer profile state stores. |
| `brain/memory/` | Agent learning memory storage. Persists fraud analysis history and pattern feedback in JSON format. |
| `agents/__pycache__/` | Python bytecode cache for agent modules. Auto-generated for performance optimization. |

---

## Table 11: Documentation Files

| Document | Purpose |
|----------|---------|
| `README.md` | Main project documentation with setup instructions, architecture overview, and quick start guide. |
| `DATASET_EDA.md` | Dataset description and exploratory data analysis with transaction schemas and statistics. |
| `DFD_MODULES.md` | Data Flow Diagrams (Level 0/1/2) and detailed module functional descriptions. |
| `KTABLE_VELOCITY.md` | KTable and velocity window implementation documentation explaining rapid-fire detection. |
| `STREAMING_CONTEXT.md` | Streaming context store documentation with velocity tracking and anomaly detection details. |
| `INTELLIGENT_ROUTING.md` | Intelligent routing logic documentation explaining decision routing to Kafka topics. |
| `PRODUCTION_SYSTEM.md` | Production coordinator documentation with 5-agent architecture and weighted voting. |
| `COMPLETE_SYSTEM.md` | Complete system overview with all components and their interactions. |
| `DEMO_GUIDE.md` | Interactive demo guide with scenario descriptions and expected results. |
| `QUICKSTART.md` | Quick start guide for running the fraud detection demo in minutes. |

---

## Summary: Component Count by Category

| Category | Count |
|----------|-------|
| Core Application | 5 |
| AI Agents | 10 |
| Kafka Streaming | 6 |
| State Management | 4 |
| Orchestration | 3 |
| Visualization | 1 |
| Infrastructure | 5 |
| Testing | 3 |
| Utilities | 2 |
| Documentation | 10 |
| **Total** | **49** |

---

## Component Dependency Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTRY POINTS                                      │
│  fraud_demo.py ──────────────────────────────────────────────────────────┐  │
│  run.py ──────────────────────────────────────────────────────────────┐  │  │
└───────────────────────────────────────────────────────────────────────│──│──┘
                                                                        │  │
                                                                        ▼  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COORDINATORS                                        │
│  production_coordinator.py ◀──────────────────────────────────────────────  │
│         │                                                                    │
│         ├──▶ agents/behavior_analyst.py                                     │
│         ├──▶ agents/pattern_detector_v2.py                                  │
│         ├──▶ agents/geographic_analyst.py                                   │
│         ├──▶ agents/risk_assessor.py                                        │
│         ├──▶ agents/temporal_analyst.py                                     │
│         │                                                                    │
│         ▼                                                                    │
│  velocity_ktable.py ◀─────────────────────────────────────────────────────  │
│         │                                                                    │
│         ├──▶ RocksDB (ktable_state/)                                        │
│         │                                                                    │
│         ▼                                                                    │
│  intelligent_router.py ──────────────────────────────────────────────────── │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KAFKA TOPICS                                        │
│  fraud-alerts ◄────┬──── human-review ◄────┬──── approved-transactions      │
└────────────────────┴──────────────────────┴─────────────────────────────────┘
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-22  
**Total Components:** 49 files across 10 categories
