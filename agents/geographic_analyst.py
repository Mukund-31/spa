"""
Geographic Analyst Agent - Specializes in location impossibility and travel time analysis
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent


class GeographicAnalystAgent(BaseAgent):
    """Agent specialized in geographic analysis and location impossibility detection"""
    
    def __init__(self):
        super().__init__(
            name="GeographicAnalyst",
            role="Geographic & Location Intelligence Specialist",
            expertise="Location impossibility detection, travel time analysis, VPN/proxy detection, geographic risk assessment"
        )
    
    def get_responsibilities(self) -> str:
        return """- Detect geographic impossibilities (transactions from multiple locations in short time)
- Analyze travel time feasibility
- Identify VPN/proxy usage patterns
- Flag location hopping behavior
- Assess geographic risk factors
- Detect physically impossible transaction patterns"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze transaction for geographic anomalies
        
        Args:
            transaction: Transaction data dictionary
            context: Streaming context with location patterns
            
        Returns:
            Dictionary with analysis results
        """
        streaming_context = context.get('streaming_context', {}) if context else {}
        velocity = streaming_context.get('velocity', {})
        profile = streaming_context.get('profile', {})
        anomalies = streaming_context.get('anomalies', {})
        risk_indicators = streaming_context.get('risk_indicators', {})
        
        prompt = f"""{self.get_system_prompt()}

Analyze this transaction for GEOGRAPHIC ANOMALIES and LOCATION IMPOSSIBILITIES:

Transaction Details:
- ID: {transaction['transaction_id']}
- Amount: INR {transaction['amount']:,.2f}
- Location: {transaction['location']}
- Merchant: {transaction['merchant_name']}
- Time: {transaction['timestamp']}

STREAMING INTELLIGENCE (Geographic Context):
- Velocity: {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes
- Unique Locations in Window: {velocity.get('unique_locations', 0)}
- Customer's Known Locations: {', '.join(profile.get('locations', [])[:5])}
- Location is New: {anomalies.get('location_is_new', False)}
- Location Hopping Detected: {risk_indicators.get('location_hopping', False)}

KNOWN FRAUD PATTERNS (LEARNING FROM HISTORY):
{context.get('fraud_patterns', 'None')}
Check if this matches any previously detected fraud patterns.

Provide your analysis in JSON format:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<detailed geographic analysis>",
    "key_findings": ["finding1", "finding2", "finding3"],
    "geographic_indicators": {{
        "location_impossibility": <boolean>,
        "travel_time_violation": <boolean>,
        "vpn_proxy_suspected": <boolean>,
        "location_hopping": <boolean>
    }}
}}

Focus on:
1. Is it physically possible to be in this location given recent transactions?
2. Does the location pattern suggest VPN/proxy usage?
3. Is there location hopping (multiple locations in short time)?
4. How does this location compare to customer's normal patterns?

CRITICAL: If {velocity.get('unique_locations', 0)} unique locations in {velocity.get('time_span_minutes', 0):.1f} minutes, 
this is PHYSICALLY IMPOSSIBLE and indicates fraud (likely automated attack with proxies)."""

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
                'geographic_indicators': {
                    'location_impossibility': False,
                    'travel_time_violation': False,
                    'vpn_proxy_suspected': False,
                    'location_hopping': False
                }
            }
