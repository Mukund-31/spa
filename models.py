"""
Data models for transactions and fraud analysis
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class Transaction:
    """Represents a financial transaction"""
    transaction_id: str
    timestamp: str
    customer_id: str
    amount: float
    currency: str
    merchant_name: str
    merchant_category: str
    location: str
    payment_method: str
    
    def to_json(self) -> str:
        """Convert transaction to JSON string"""
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str) -> 'Transaction':
        """Create transaction from JSON string"""
        data = json.loads(json_str)
        return Transaction(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentAnalysis:
    """Represents an individual agent's analysis"""
    agent_name: str
    analysis: str
    score: float
    confidence: float
    key_findings: list
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class FraudDecision:
    """Final fraud detection decision from multi-agent system"""
    transaction_id: str
    final_score: float
    decision: str  # 'APPROVE', 'REVIEW', 'REJECT'
    risk_analyst_score: float
    pattern_detective_score: float
    decision_maker_reasoning: str
    agent_discussion: list  # List of agent messages
    timestamp: str
    
    def to_json(self) -> str:
        """Convert decision to JSON string"""
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str) -> 'FraudDecision':
        """Create decision from JSON string"""
        data = json.loads(json_str)
        return FraudDecision(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)
