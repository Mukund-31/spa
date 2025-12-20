"""
Risk Assessor Agent - Specializes in financial risk and amount deviation analysis
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent


class RiskAssessorAgent(BaseAgent):
    """Agent specialized in financial risk assessment and amount deviation"""
    
    def __init__(self):
        super().__init__(
            name="RiskAssessor",
            role="Financial Risk Assessment Specialist",
            expertise="Amount deviation analysis, financial risk scoring, merchant category risk, spending pattern analysis"
        )
    
    def get_responsibilities(self) -> str:
        return """- Assess financial risk of transaction amount
- Calculate amount deviation from customer baseline
- Evaluate merchant category risk
- Analyze spending pattern anomalies
- Apply velocity multipliers to risk
- Detect progressive amount testing patterns"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for financial risk
        
        Args:
            transaction: Transaction data dictionary
            context: Streaming context with financial metrics
            
        Returns:
            Dictionary with analysis results
        """
        streaming_context = context.get('streaming_context', {}) if context else {}
        velocity = streaming_context.get('velocity', {})
        profile = streaming_context.get('profile', {})
        anomalies = streaming_context.get('anomalies', {})
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for FINANCIAL RISK and AMOUNT DEVIATION:

Transaction Details:
- ID: {transaction['transaction_id']}
- Amount: INR {transaction['amount']:,.2f}
- Merchant: {transaction['merchant_name']} ({transaction['merchant_category']})
- Payment Method: {transaction['payment_method']}

STREAMING INTELLIGENCE (Financial Context):
- Customer Average: INR {profile.get('avg_amount', 0):.2f}
- Total Transactions: {profile.get('total_transactions', 0)}
- Amount Deviation: {anomalies.get('amount_deviation_pct', 0):.1f}%
- Velocity: {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes
- Total Amount in Window: INR {velocity.get('total_amount', 0):.2f}

KNOWN FRAUD PATTERNS (LEARNING FROM HISTORY):
{context.get('fraud_patterns', 'None')}
Check if this matches any previously detected fraud patterns.

Provide your analysis in JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed financial risk analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "financial_indicators": {{
        "amount_spike": <boolean>,
        "high_merchant_risk": <boolean>,
        "unusual_payment_method": <boolean>,
        "progressive_testing": <boolean>
    }}
}}

Focus on:
1. How does INR {transaction['amount']:,.2f} compare to customer avg INR {profile.get('avg_amount', 0):.2f}?
2. Is the {anomalies.get('amount_deviation_pct', 0):.1f}% deviation suspicious?
3. Does the merchant category pose high risk?
4. Should velocity ({velocity.get('transaction_count', 0)} txns) increase the risk score?

CRITICAL: 
- If deviation > 500% = Major amount spike
- If velocity > 10 txns = Apply velocity multiplier (1.5x risk)
- Small amounts + high velocity = Card testing pattern"""

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
                'financial_indicators': {
                    'amount_spike': False,
                    'high_merchant_risk': False,
                    'unusual_payment_method': False,
                    'progressive_testing': False
                }
            }
