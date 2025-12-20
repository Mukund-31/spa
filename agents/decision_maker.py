"""
Decision Maker Agent - Synthesizes inputs and makes final fraud determination
"""
import json
from typing import Dict
from agents.base_agent import BaseAgent
from models import Transaction


class DecisionMakerAgent(BaseAgent):
    """Agent that synthesizes analyses and makes final decision"""
    
    def __init__(self):
        super().__init__(
            name="Decision Maker",
            role="Final Decision Authority",
            expertise="Synthesis of multiple analyses, risk assessment, final fraud determination"
        )
    
    def get_responsibilities(self) -> str:
        return """- Review and synthesize Risk Analyst's findings
- Consider Pattern Detective's behavioral analysis
- Weigh all evidence and perspectives
- Make final fraud determination
- Provide clear reasoning for decision
- Recommend appropriate action (APPROVE/REVIEW/REJECT)"""
    
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Make final decision based on other agents' analyses
        
        Args:
            transaction: Transaction data dictionary
            context: Dictionary containing other agents' analyses
            
        Returns:
            Dictionary with final decision
        """
        tx = Transaction(**transaction) if isinstance(transaction, dict) else transaction
        
        # Extract other agents' analyses from context
        risk_analysis = context.get('risk_analyst', {}) if context else {}
        pattern_analysis = context.get('pattern_detective', {}) if context else {}
        
        prompt = f"""{self.get_system_prompt()}

You must make the FINAL DECISION on this transaction after reviewing analyses from two expert agents.

Transaction Details:
- ID: {tx.transaction_id}
- Amount: {tx.currency} {tx.amount:,.2f}
- Merchant: {tx.merchant_name} ({tx.merchant_category})
- Location: {tx.location}
- Payment: {tx.payment_method}
- Time: {tx.timestamp}

RISK ANALYST'S ASSESSMENT:
Score: {risk_analysis.get('score', 'N/A')}/100
Confidence: {risk_analysis.get('confidence', 'N/A')}%
Analysis: {risk_analysis.get('analysis', 'No analysis provided')}
Key Findings: {', '.join(risk_analysis.get('key_findings', []))}

PATTERN DETECTIVE'S ASSESSMENT:
Score: {pattern_analysis.get('score', 'N/A')}/100
Confidence: {pattern_analysis.get('confidence', 'N/A')}%
Analysis: {pattern_analysis.get('analysis', 'No analysis provided')}
Key Findings: {', '.join(pattern_analysis.get('key_findings', []))}

Based on both expert analyses, provide your FINAL DECISION in JSON format:
{{
    "final_score": <number 0-100>,
    "decision": "<APPROVE|REVIEW|REJECT>",
    "confidence": <number 0-100>,
    "reasoning": "<comprehensive reasoning synthesizing both analyses>",
    "key_factors": ["factor1", "factor2", "factor3"],
    "recommendation": "<specific action to take>",
    "agreement_level": "<how much the two agents agree or disagree>"
}}

Decision Guidelines:
- APPROVE (score 0-40): Low fraud risk, process normally
- REVIEW (score 41-70): Medium risk, requires human review
- REJECT (score 71-100): High fraud risk, block transaction

Consider:
1. Do the agents agree or disagree?
2. Which concerns are most critical?
3. What's the overall risk level?
4. What action best protects against fraud while minimizing false positives?"""

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
            avg_score = (risk_analysis.get('score', 50) + pattern_analysis.get('score', 50)) / 2
            decision = 'APPROVE' if avg_score < 40 else ('REVIEW' if avg_score < 70 else 'REJECT')
            
            return {
                'agent_name': self.name,
                'final_score': avg_score,
                'decision': decision,
                'confidence': 30,
                'reasoning': response,
                'key_factors': ['Unable to parse structured response'],
                'recommendation': f'Default to {decision} based on average score',
                'agreement_level': 'Unknown'
            }
