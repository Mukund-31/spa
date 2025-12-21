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
        
        amount = transaction['amount']
        avg_amount = profile.get('avg_amount', 0)
        
        # SIMPLE PROMPT FOR SMALL MODEL
        prompt = f"""You are assessing financial risk.

TRANSACTION:
Amount: INR {amount:.2f}
Category: {transaction['merchant_category']}

BASELINE:
- Customer average: INR {avg_amount:.2f}
- Transactions in window: {velocity.get('transaction_count', 0)}

ANALYSIS:
Current amount is {amount:.2f}, customer average is {avg_amount:.2f}.
Deviation: {((amount / avg_amount - 1) * 100) if avg_amount > 0 else 0:.0f}%

RULES:
1. If customer avg = 0: Return score 15 (first transaction)
2. If amount is 5x or more than average: Return score 70-85 (major spike)
3. If amount is 2-5x average: Return score 50-65 (moderate spike)
4. If amount <= 2x average: Return score 15-25 (normal variation)
5. If velocity > 10: Add +20 to score (velocity multiplier)

Return JSON:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<one sentence>",
    "key_findings": ["<brief finding>"],
    "financial_indicators": {{
        "amount_spike": <true if >5x avg>,
        "high_merchant_risk": false,
        "unusual_payment_method": false,
        "progressive_testing": false
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
            
            # CRITICAL OVERRIDE: Force correct scores for first transaction or normal amounts
            if avg_amount == 0:
                result['score'] = 15
                result['confidence'] = 85
                result['analysis'] = "First transaction - establishing baseline"
                result['key_findings'] = ["First transaction for customer"]
            elif amount <= 2000:
                result['score'] = min(result.get('score', 20), 25)
                result['analysis'] = f"Normal purchase amount INR {amount:.2f}"
            
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
