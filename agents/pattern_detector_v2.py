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
        profile = streaming_context.get('profile', {})
        risk_indicators = streaming_context.get('risk_indicators', {})
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for ATTACK PATTERNS and FRAUD SIGNATURES:

Transaction Details:
- ID: {transaction['transaction_id']}
- Amount: INR {transaction['amount']:,.2f}
- Merchant: {transaction['merchant_name']} ({transaction['merchant_category']})
- Customer: {transaction['customer_id']}

STREAMING INTELLIGENCE (Pattern Context):
- Velocity: {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes
- Average Amount in Window: INR {velocity.get('avg_amount', 0):.2f}
- Unique Merchants: {velocity.get('unique_merchants', 0)}
- Customer Risk Level: {profile.get('total_transactions', 0)} total transactions
- Merchant Hopping: {risk_indicators.get('merchant_hopping', False)}

KNOWN FRAUD PATTERNS (LEARNING FROM HISTORY):
{context.get('fraud_patterns', 'None')}
Check if this matches any previously detected fraud patterns.

Provide your analysis in JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed pattern analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "pattern_indicators": {{
        "card_testing": <boolean>,
        "progressive_amounts": <boolean>,
        "attack_signature_match": <boolean>,
        "coordinated_attack": <boolean>
    }}
}}

Focus on:
1. Does this match card testing pattern (small amounts + high velocity)?
2. Is there progressive amount testing (increasing amounts over time)?
3. Does the pattern match known fraud signatures?
4. Is this part of a coordinated attack?

CRITICAL PATTERNS:
- Card Testing: Small amounts (< INR 100) + velocity > 10 txns
- Progressive Testing: Amounts increasing (₹10 → ₹50 → ₹100 → ₹500)
- Merchant Hopping: {velocity.get('unique_merchants', 0)} merchants in short time
- Rapid Fire: {velocity.get('transaction_count', 0)} txns in {velocity.get('time_span_minutes', 0):.1f} min"""

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
