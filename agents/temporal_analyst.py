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
        
        # Get context
        tx_count = velocity.get('transaction_count', 0)
        vel_score = velocity.get('velocity_score', 0)
        time_span = velocity.get('time_span_minutes', 0)
        
        # INTELLIGENT PROMPT
        prompt = f"""You are detecting automated/scripted behavior in transactions.

TIMING CONTEXT:
- Transactions: {tx_count} in {time_span:.1f} minutes
- Velocity: {vel_score:.2f} transactions/minute
- Time between transactions: {(time_span / tx_count if tx_count > 0 else 0):.1f} minutes average

ANALYSIS:
Evaluate if this shows automated behavior:
- Human behavior: Usually < 1 transaction/minute, irregular timing
- Bot/script: Usually > 1 transaction/minute, regular intervals
- Current velocity {vel_score:.2f} txn/min suggests {"automated behavior" if vel_score > 1.5 else "human behavior" if vel_score < 1.0 else "borderline"}

Consider:
- {tx_count} transactions in {time_span:.1f} minutes
- Regular intervals suggest scripted behavior
- Irregular timing suggests human

Return JSON with your assessment:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<explain your reasoning>",
    "key_findings": ["<key observation>"],
    "temporal_indicators": {{
        "scripted_behavior": <true/false>,
        "regular_intervals": <true/false>,
        "unusual_hours": false,
        "high_frequency": <true/false>
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
            
            # CRITICAL OVERRIDE: Force correct scores for low velocity
            tx_count = velocity.get('transaction_count', 0)
            vel_score = velocity.get('velocity_score', 0)
            if tx_count <= 1:
                result['score'] = 10
                result['confidence'] = 85
                result['analysis'] = "Single transaction - no timing pattern detected"
                result['key_findings'] = ["Insufficient data for temporal analysis"]
                result['temporal_indicators'] = {
                    'scripted_behavior': False,
                    'regular_intervals': False,
                    'unusual_hours': False,
                    'high_frequency': False
                }
            elif vel_score < 1.0:
                result['score'] = min(result.get('score', 20), 20)
                result['analysis'] = "Low velocity - human behavior pattern"
            
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
