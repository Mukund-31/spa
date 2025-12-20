"""
Temporal Analyst Agent - Specializes in transaction timing and scripted behavior detection
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent


class TemporalAnalystAgent(BaseAgent):
    """Agent specialized in temporal patterns and scripted behavior detection"""
    
    def __init__(self):
        super().__init__(
            name="TemporalAnalyst",
            role="Temporal Pattern & Timing Specialist",
            expertise="Transaction timing analysis, scripted behavior detection, time-based anomalies, automated attack patterns"
        )
    
    def get_responsibilities(self) -> str:
        return """- Analyze transaction timing patterns
- Detect scripted/automated behavior (regular intervals)
- Identify unusual transaction hours
- Flag bot-like timing patterns
- Detect time-based attack signatures
- Analyze transaction frequency patterns"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for temporal patterns and scripted behavior
        
        Args:
            transaction: Transaction data dictionary
            context: Streaming context with timing information
            
        Returns:
            Dictionary with analysis results
        """
        streaming_context = context.get('streaming_context', {}) if context else {}
        velocity = streaming_context.get('velocity', {})
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for TEMPORAL PATTERNS and SCRIPTED BEHAVIOR:

Transaction Details:
- ID: {transaction['transaction_id']}
- Amount: INR {transaction['amount']:,.2f}
- Timestamp: {transaction['timestamp']}
- Merchant: {transaction['merchant_name']}

STREAMING INTELLIGENCE (Temporal Context):
- Transaction Count: {velocity.get('transaction_count', 0)} in {velocity.get('time_span_minutes', 0):.1f} minutes
- Velocity Score: {velocity.get('velocity_score', 0):.2f} transactions/minute
- Time Span: {velocity.get('time_span_minutes', 0):.1f} minutes

- Time Span: {velocity.get('time_span_minutes', 0):.1f} minutes

KNOWN FRAUD PATTERNS (LEARNING FROM HISTORY):
{context.get('fraud_patterns', 'None')}
Check if this matches any previously detected fraud patterns.

Provide your analysis in JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed temporal analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "temporal_indicators": {{
        "scripted_behavior": <boolean>,
        "regular_intervals": <boolean>,
        "unusual_hours": <boolean>,
        "high_frequency": <boolean>
    }}
}}

Focus on:
1. Does the transaction frequency suggest automated/scripted behavior?
2. Are transactions occurring at regular intervals (e.g., every 12 seconds)?
3. Is the transaction time unusual (e.g., 3 AM)?
4. Does the velocity ({velocity.get('velocity_score', 0):.2f} txns/min) indicate automation?

CRITICAL PATTERNS:
- If velocity > 1.0 txn/min = Likely automated
- If {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} min = High frequency attack
- Regular intervals = Scripted bot behavior"""

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
                'temporal_indicators': {
                    'scripted_behavior': False,
                    'regular_intervals': False,
                    'unusual_hours': False,
                    'high_frequency': False
                }
            }
