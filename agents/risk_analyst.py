"""
Risk Analyst Agent - Focuses on financial risk assessment
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent
from models import Transaction, AgentAnalysis


class RiskAnalystAgent(BaseAgent):
    """Agent specialized in financial risk assessment"""
    
    def __init__(self):
        super().__init__(
            name="Risk Analyst",
            role="Financial Risk Assessment Specialist",
            expertise="Transaction amount analysis, spending patterns, merchant risk evaluation, geographic risk factors"
        )
    
    def get_responsibilities(self) -> str:
        return """- Evaluate transaction amounts for anomalies
- Assess merchant category risk levels
- Analyze geographic risk factors
- Identify unusual spending patterns
- Compare transaction to typical customer behavior
- Flag high-risk currencies or locations"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction from financial risk perspective
        
        Args:
            transaction: Transaction data dictionary
            context: Additional context (not used in initial analysis)
            
        Returns:
            Dictionary with analysis results
        """
        tx = Transaction(**transaction) if isinstance(transaction, dict) else transaction
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for FINANCIAL RISK:

Transaction Details:
- ID: {tx.transaction_id}
- Amount: {tx.currency} {tx.amount:,.2f}
- Merchant: {tx.merchant_name}
- Category: {tx.merchant_category}
- Location: {tx.location}
- Payment Method: {tx.payment_method}
- Time: {tx.timestamp}

Provide your analysis in the following JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed financial risk analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "risk_factors": {{
        "amount_risk": <number 0-100>,
        "merchant_risk": <number 0-100>,
        "location_risk": <number 0-100>,
        "payment_method_risk": <number 0-100>
    }}
}}

Focus on:
1. Is the transaction amount unusual or suspicious?
2. Is the merchant category high-risk?
3. Are there geographic red flags?
4. Does the payment method raise concerns?"""

        response = self.generate_response(prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            response_clean = response.strip()
            if response_clean.startswith('```'):
                # Remove markdown code block markers
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
                'risk_factors': {
                    'amount_risk': 50,
                    'merchant_risk': 50,
                    'location_risk': 50,
                    'payment_method_risk': 50
                }
            }
