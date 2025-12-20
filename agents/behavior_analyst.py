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
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for VELOCITY PATTERNS and AUTOMATED BEHAVIOR:

Transaction Details:
- ID: {transaction['transaction_id']}
- Amount: INR {transaction['amount']:,.2f}
- Customer: {transaction['customer_id']}
- Merchant: {transaction['merchant_name']} ({transaction['merchant_category']})
- Time: {transaction['timestamp']}

STREAMING INTELLIGENCE (Critical Context):
- Velocity: {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes
- Customer Baseline: {profile.get('total_transactions', 0)} total transactions, avg INR {profile.get('avg_amount', 0):.2f}
- Velocity Score: {velocity.get('velocity_score', 0):.2f} transactions/minute
- Unique Locations: {velocity.get('unique_locations', 0)}
- Unique Merchants: {velocity.get('unique_merchants', 0)}

PREVIOUSLY DETECTED FRAUD PATTERNS (LEARNING CONTEXT):
{context.get('fraud_patterns', 'None')}
Check if this transaction matches any of these known fraud patterns.

Provide your analysis in JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed velocity and behavior analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "velocity_indicators": {{
        "high_velocity": <boolean>,
        "automated_behavior": <boolean>,
        "rapid_fire_attack": <boolean>,
        "bot_like_pattern": <boolean>
    }}
}}

Focus on:
1. Is the velocity (transactions/minute) unusual for this customer?
2. Does the pattern suggest automated/scripted behavior?
3. Is this a rapid-fire attack (many transactions in short time)?
4. How does this compare to customer's normal behavior?"""

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
