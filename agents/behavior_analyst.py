"""
Behavior Analyst Agent - Specializes in velocity patterns and automated behavior detection
"""
import json
import re
from typing import Dict
from agents.base_agent import BaseAgent
from colorama import Fore, Style


class BehaviorAnalystAgent(BaseAgent):
    """Agent specialized in velocity patterns and automated behavior"""
    
    def __init__(self):
        super().__init__(
            name="BehaviorAnalyst",
            role="Velocity Pattern & Automated Behavior Specialist",
            expertise="Transaction velocity analysis, automated behavior detection, customer baseline comparison"
        )
    
    def get_responsibilities(self) -> str:
        return """- Analyze transaction velocity patterns
- Detect automated/scripted behavior
- Compare against customer baseline behavior
- Identify rapid-fire transaction attacks
- Flag unusual transaction frequency
- Detect bot-like behavior patterns"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for velocity patterns and automated behavior
        
        Args:
            transaction: Transaction data dictionary
            context: Streaming context with velocity metrics
            
        Returns:
            Dictionary with analysis results
        """
        streaming_context = context.get('streaming_context', {}) if context else {}
        velocity = streaming_context.get('velocity', {})
        profile = streaming_context.get('profile', {})
        
        # Get context data
        tx_count = velocity.get('transaction_count', 0)
        avg_amount = profile.get('avg_amount', 0)
        
        # SIMPLE PROMPT FOR SMALL MODEL
        prompt = f"""You are a fraud detection agent analyzing transaction velocity.

TRANSACTION:
Amount: INR {transaction['amount']:,.2f}
Merchant: {transaction['merchant_name']} ({transaction['merchant_category']})

VELOCITY DATA:
- Transactions in last 5 min: {tx_count}
- Customer's average amount: INR {avg_amount:.2f}

CONTEXT ANALYSIS:
- This is transaction #{tx_count} in the current window
- Customer baseline: {avg_amount:.2f} INR average

RULES:
1. If transactions = 0 or 1: Return score 10-15 (insufficient data)
2. If transactions = 2-5: Return score 20-35 (low velocity, normal)
3. If transactions = 6-10: Return score 40-60 (moderate velocity, watch)
4. If transactions > 10: Return score 70-90 (high velocity, suspicious)

Return JSON:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<explain your reasoning in one sentence>",
    "key_findings": ["<key observation>"],
    "velocity_indicators": {{
        "high_velocity": <true if >10 txns>,
        "automated_behavior": <true if >10 txns>,
        "rapid_fire_attack": <true if >15 txns>,
        "bot_like_pattern": <true if >10 txns>
    }}
}}"""

        response = self.generate_response(prompt)
        
        try:
            # Clean the response
            response_clean = response.strip()
            
            # Remove markdown code blocks if present
            if response_clean.startswith('```'):
                lines = response_clean.split('\n')
                response_clean = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_clean
                if response_clean.startswith('json'):
                    response_clean = response_clean[4:].strip()
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_clean)
            if json_match:
                response_clean = json_match.group(0)
            
            result = json.loads(response_clean)
            result['agent_name'] = self.name
            
            # Cap score for first transaction
            if avg_amount == 0:
                result['score'] = min(result.get('score', 15), 20)
                result['analysis'] = "First transaction for customer - establishing baseline"
            
            return result
            
        except (json.JSONDecodeError, AttributeError) as e:
            # If parsing fails, extract scores from text
            print(f"  {Fore.YELLOW}Note: Parsing response as text (AI didn't return JSON){Style.RESET_ALL}")
            
            # Try to extract score from response text
            import re
            score_match = re.search(r'score["\s:]*(\d+)', response.lower())
            confidence_match = re.search(r'confidence["\s:]*(\d+)', response.lower())
            
            score = int(score_match.group(1)) if score_match else 50
            confidence = int(confidence_match.group(1)) if confidence_match else 70
            
            return {
                'agent_name': self.name,
                'score': score,
                'confidence': confidence,
                'analysis': response[:200],  # First 200 chars
                'key_findings': [response[:100]],
                'velocity_indicators': {
                    'high_velocity': 'high velocity' in response.lower(),
                    'automated_behavior': 'automated' in response.lower() or 'bot' in response.lower(),
                    'rapid_fire_attack': 'rapid' in response.lower(),
                    'bot_like_pattern': 'bot' in response.lower() or 'script' in response.lower()
                }
            }
