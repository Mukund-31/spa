"""
Configuration management for Kafka Fraud Detection System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.5-flash-lite'

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9093')
KAFKA_TOPIC_TRANSACTIONS = os.getenv('KAFKA_TOPIC_TRANSACTIONS', 'transactions')
KAFKA_TOPIC_FRAUD_ALERTS = os.getenv('KAFKA_TOPIC_FRAUD_ALERTS', 'fraud-alerts')
KAFKA_TOPIC_LEGITIMATE = os.getenv('KAFKA_TOPIC_LEGITIMATE', 'legitimate-transactions')

# Transaction Generation Configuration
TRANSACTION_RATE = float(os.getenv('TRANSACTION_RATE', '2'))  # transactions per second
SUSPICIOUS_TRANSACTION_RATIO = float(os.getenv('SUSPICIOUS_TRANSACTION_RATIO', '0.1'))  # 10% suspicious

# Fraud Detection Thresholds
FRAUD_THRESHOLD_HIGH = 70  # Score above this goes to fraud-alerts
FRAUD_THRESHOLD_LOW = 30   # Score below this is likely legitimate

# Agent Configuration
AGENT_TEMPERATURE = 0.7
AGENT_MAX_TOKENS = 1000
