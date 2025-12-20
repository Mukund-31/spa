"""
Intelligent Router - Layer 3: Confidence-Based Routing
Routes fraud decisions to appropriate Kafka topics based on confidence and risk score
"""
import json
from typing import Dict
from kafka import KafkaProducer
from colorama import Fore, Style
import config


class IntelligentRouter:
    """Routes fraud decisions to appropriate topics with feedback loop"""
    
    def __init__(self):
        """Initialize Kafka producer for routing"""
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Define topics
        self.FRAUD_ALERTS = "fraud-alerts"
        self.HUMAN_REVIEW = "human-review"
        self.APPROVED_TRANSACTIONS = "approved-transactions"
        self.ANALYST_FEEDBACK = "analyst-feedback"
        
        # Initialize Knowledge Base (File API simulation)
        from knowledge_base import KnowledgeBase
        self.kb = KnowledgeBase()
    
    def route_decision(self, decision: Dict, confidence: float) -> str:
        """
        Route decision to appropriate topic based on confidence and risk score
        
        Args:
            decision: FraudDecision object as dict
            confidence: Confidence level (0-100)
            
        Returns:
            Topic name where decision was routed
        """
        final_score = decision.get('final_score', 50)
        
        # Routing logic - FIXED to use actual confidence
        if final_score > 80 and confidence > 70:
            # High confidence fraud - auto-block
            topic = self.FRAUD_ALERTS
            routing_reason = "HIGH-CONFIDENCE FRAUD → AUTO-BLOCK"
            action = "Immediate block, no human review needed"
            color = Fore.RED
            
        elif final_score > 30:
            # Medium risk OR low confidence - needs analyst review
            topic = self.HUMAN_REVIEW
            routing_reason = "UNCERTAIN → HUMAN REVIEW"
            action = "Flagged for manual investigation"
            color = Fore.YELLOW
            
        else:
            # Low risk - auto-approve
            topic = self.APPROVED_TRANSACTIONS
            routing_reason = "LOW RISK → AUTO-APPROVE"
            action = "Transaction approved automatically"
            color = Fore.GREEN
        
        # Add routing metadata
        routed_decision = {
            **decision,
            'routing': {
                'topic': topic,
                'reason': routing_reason,
                'action': action,
                'confidence': confidence,
                'timestamp': decision.get('timestamp')
            }
        }
        
        # Publish to appropriate topic
        self.producer.send(
            topic,
            key=decision.get('transaction_id'),
            value=routed_decision
        )
        self.producer.flush()
        
        # Print routing decision with ACTUAL confidence
        print(f"\n{color}📤 ROUTING DECISION:{Style.RESET_ALL}")
        print(f"{color}  ✓ {routing_reason}{Style.RESET_ALL}")
        print(f"  • Topic: {topic}")
        print(f"  • Action: {action}")
        print(f"  • Confidence: {confidence:.0f}%")  # Use passed confidence
        print(f"  • Risk Score: {final_score:.1f}%\n")
        
        # Log decision to Knowledge Base (Feedback Loop)
        self.kb.add_feedback(routed_decision)
        
        return topic
    
    def process_analyst_feedback(self, feedback: Dict):
        """
        Process feedback from human analysts for learning loop
        
        Args:
            feedback: {
                'transaction_id': str,
                'original_decision': str,
                'analyst_decision': str,  # 'FRAUD' or 'LEGITIMATE'
                'analyst_notes': str,
                'correction_needed': bool
            }
        """
        # Publish to analyst feedback topic for learning loop
        self.producer.send(
            self.ANALYST_FEEDBACK,
            key=feedback.get('transaction_id'),
            value=feedback
        )
        self.producer.flush()
        
        print(f"{Fore.CYAN}📝 ANALYST FEEDBACK RECEIVED:{Style.RESET_ALL}")
        print(f"  Transaction: {feedback.get('transaction_id')}")
        print(f"  Original: {feedback.get('original_decision')}")
        print(f"  Analyst: {feedback.get('analyst_decision')}")
        
        if feedback.get('correction_needed'):
            print(f"{Fore.YELLOW}  ⚠️  Correction needed - updating agent knowledge{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}  ✓ Decision confirmed{Style.RESET_ALL}")
    
    def get_routing_statistics(self) -> Dict:
        """Get routing statistics"""
        return {
            'topics': {
                'fraud_alerts': self.FRAUD_ALERTS,
                'human_review': self.HUMAN_REVIEW,
                'approved_transactions': self.APPROVED_TRANSACTIONS,
                'analyst_feedback': self.ANALYST_FEEDBACK
            },
            'routing_rules': {
                'auto_block': 'score > 80 AND confidence > 70',
                'human_review': '30 < score <= 80',
                'auto_approve': 'score <= 30'
            }
        }
