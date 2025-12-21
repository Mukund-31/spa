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
        
        # Get context
        unique_locs = velocity.get('unique_locations', 0)
        time_span = velocity.get('time_span_minutes', 0)
        
        # INTELLIGENT PROMPT
        prompt = f"""You are analyzing transaction location patterns.

TRANSACTION:
Location: {transaction['location']}

GEOGRAPHIC CONTEXT:
- Unique locations in window: {unique_locs}
- Time span: {time_span:.1f} minutes
- Transaction count: {velocity.get('transaction_count', 0)}

ANALYSIS:
Evaluate geographic risk:
- {unique_locs} location(s) in {time_span:.1f} minutes
- Is it physically possible to be in {unique_locs} different locations in {time_span:.1f} minutes?
- Single location = normal behavior
- Multiple locations in short time = suspicious (VPN/proxy or impossible travel)

Return JSON with your assessment:
{{
    "score": <number 0-100>,
    "confidence": <number 0-100>,
    "analysis": "<explain your reasoning>",
    "key_findings": ["<key observation>"],
    "geographic_indicators": {{
        "location_impossibility": <true/false>,
        "travel_time_violation": <true/false>,
        "vpn_proxy_suspected": <true/false>,
        "location_hopping": <true/false>
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
            
            # CRITICAL OVERRIDE: Force correct scores for single location
            unique_locs = velocity.get('unique_locations', 0)
            if unique_locs <= 1:
                result['score'] = 10
                result['confidence'] = 90
                result['analysis'] = "Single location - no geographic anomaly detected"
                result['key_findings'] = ["Transaction from single location - normal"]
                result['geographic_indicators'] = {
                    'location_impossibility': False,
                    'travel_time_violation': False,
                    'vpn_proxy_suspected': False,
                    'location_hopping': False
                }
            
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
