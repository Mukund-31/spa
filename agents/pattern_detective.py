"""
Pattern Detective Agent - Specializes in behavioral pattern recognition
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent
from models import Transaction


class PatternDetectiveAgent(BaseAgent):
    """Agent specialized in behavioral pattern detection"""
    
    def __init__(self):
        super().__init__(
            name="Pattern Detective",
            role="Behavioral Pattern Recognition Specialist",
            expertise="Transaction velocity, time-based anomalies, location patterns, behavioral analysis"
        )
    
    def get_responsibilities(self) -> str:
        return """- Detect unusual transaction timing patterns
- Identify velocity anomalies (rapid successive transactions)
- Analyze location inconsistencies
- Spot payment method switching patterns
- Recognize behavioral red flags
- Identify patterns common in fraud cases"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for behavioral patterns
        
        Args:
            transaction: Transaction data dictionary
            context: Additional context (not used in initial analysis)
            
        Returns:
            Dictionary with analysis results
        """
        tx = Transaction(**transaction) if isinstance(transaction, dict) else transaction
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for BEHAVIORAL PATTERNS and ANOMALIES:

Transaction Details:
- ID: {tx.transaction_id}
- Customer: {tx.customer_id}
- Time: {tx.timestamp}
- Amount: {tx.currency} {tx.amount:,.2f}
- Location: {tx.location}
- Merchant: {tx.merchant_name} ({tx.merchant_category})
- Payment: {tx.payment_method}

Provide your analysis in the following JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed behavioral pattern analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "pattern_flags": {{
        "timing_anomaly": <number 0-100>,
        "location_anomaly": <number 0-100>,
        "velocity_concern": <number 0-100>,
        "behavioral_red_flags": <number 0-100>
    }},
    "suspicious_patterns": ["pattern1", "pattern2"]
}}

Focus on:
1. Is the transaction timing unusual (odd hours, rapid succession)?
2. Are there location-based red flags?
3. Does the behavior match typical fraud patterns?
4. Are there velocity concerns (too many transactions too quickly)?"""

        response = self.generate_response(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_clean = response.strip()
            if response_clean.startswith('```'):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_clean
                if response_clean.startswith('json'):
                    response_clean = response_clean[4:].strip()
            
            result = json.loads(response_clean)
            
            # Add agent metadata
            result['agent_name'] = self.name
            
            return result
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'agent_name': self.name,
                'score': 50,
                'confidence': 30,
                'analysis': response,
                'key_findings': ['Unable to parse structured response'],
                'pattern_flags': {
                    'timing_anomaly': 50,
                    'location_anomaly': 50,
                    'velocity_concern': 50,
                    'behavioral_red_flags': 50
                },
                'suspicious_patterns': []
            }
