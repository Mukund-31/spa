"""
Pattern Detector V2 Agent - Specializes in card testing and progressive attack patterns
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent


class PatternDetectorV2Agent(BaseAgent):
    """Agent specialized in card testing and progressive attack pattern detection"""
    
    def __init__(self):
        super().__init__(
            name="PatternDetector",
            role="Attack Pattern Recognition Specialist",
            expertise="Card testing detection, progressive amount patterns, attack signature matching, fraud pattern recognition"
        )
    
    def get_responsibilities(self) -> str:
        return """- Detect card testing attack patterns
- Identify progressive amount testing (₹10 → ₹50 → ₹100 → ₹500)
- Match known fraud attack signatures
- Recognize account takeover patterns
- Detect coordinated attack patterns
- Identify bot-driven fraud campaigns"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for attack patterns
        
        Args:
            transaction: Transaction data dictionary
            context: Streaming context with pattern information
            
        Returns:
            Dictionary with analysis results
        """
        streaming_context = context.get('streaming_context', {}) if context else {}
        velocity = streaming_context.get('velocity', {})
        
        # Get context
        tx_count = velocity.get('transaction_count', 0)
        unique_merchants = velocity.get('unique_merchants', 0)
        
        # INTELLIGENT PROMPT
        prompt = f"""You are detecting fraud patterns in transactions.

TRANSACTION:
Amount: INR {transaction['amount']:,.2f}
Merchant: {transaction['merchant_name']}

PATTERN CONTEXT:
- Transactions in window: {tx_count}
- Unique merchants: {unique_merchants}
- Average amount in window: INR {velocity.get('avg_amount', 0):.2f}

ANALYSIS:
Evaluate if this shows fraud patterns:
- Card testing: Multiple small transactions to test if card works
- Progressive amounts: Amounts increasing over time (₹10→₹50→₹100)
- Merchant hopping: Many different merchants in short time

Consider:
- {tx_count} transactions suggests {"high velocity pattern" if tx_count > 10 else "normal activity" if tx_count > 1 else "insufficient data"}
- {unique_merchants} merchants suggests {"merchant hopping" if unique_merchants > 3 else "normal"}
- Amount {transaction['amount']:.2f} is {"small (card testing?)" if transaction['amount'] < 100 else "normal"}

Return JSON with your risk assessment (0-100):
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<explain your reasoning>",
    "key_findings": ["<key observation>"],
    "pattern_indicators": {{
        "card_testing": <true/false>,
        "progressive_amounts": <true/false>,
        "attack_signature_match": false,
        "coordinated_attack": <true/false>
    }}
}}"""

        response = self.generate_response(prompt)
        
        try:
            response_clean = response.strip()
            if response_clean.startswith('```'):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_clean
                if response_clean.startswith('json'):
                    response_clean = response_clean[4:].strip()
            
            result = json.loads(response_clean)
            result['agent_name'] = self.name
            
            # CRITICAL OVERRIDE: Force correct scores for zero-context scenarios
            tx_count = velocity.get('transaction_count', 0)
            if tx_count <= 1:
                result['score'] = 10
                result['confidence'] = 80
                result['analysis'] = "Insufficient data - single transaction, no pattern possible"
                result['key_findings'] = ["Single transaction - no pattern detection possible"]
                result['pattern_indicators'] = {
                    'card_testing': False,
                    'progressive_amounts': False,
                    'attack_signature_match': False,
                    'coordinated_attack': False
                }
            
            return result
            
        except json.JSONDecodeError:
            return {
                'agent_name': self.name,
                'score': 50,
                'confidence': 30,
                'analysis': response,
                'key_findings': ['Unable to parse structured response'],
                'pattern_indicators': {
                    'card_testing': False,
                    'progressive_amounts': False,
                    'attack_signature_match': False,
                    'coordinated_attack': False
                }
            }
