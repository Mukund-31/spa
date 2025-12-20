"""
Fraud Generator Agent (The Adversary)
Uses Ollama to generate sophisticated fraud attempts based on what has been caught before.
"""
from agents.base_agent import BaseAgent
from typing import Dict, List
import json
import random

class FraudGeneratorAgent(BaseAgent):
    def __init__(self, model_name="qwen2.5:0.5b"):
        super().__init__(
            name="Fraudster", 
            role="Red Team Adversary",
            expertise="Financial fraud simulation and evasion strategies"
        )
        self.model = model_name

    def get_responsibilities(self) -> str:
        return "Generate adversarial fraud scenarios to test system robustness"

    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """Not utilized for Fraudster, but required by BaseAgent interface"""
        return {"score": 0, "confidence": 0, "analysis": "N/A (Adversary)"}
    
    def generate_attack(self, recent_failures: List[Dict]) -> Dict:
        """
        Generate a new fraud scenario trying to evade detection
        """
        # Summarize what failed
        failures_summary = ""
        if recent_failures:
            failures_summary = "My previous attempts were caught:\n"
            for fail in recent_failures[-3:]: # Look at last 3 failures
                failures_summary += f"- Pattern: {fail.get('pattern_desc', 'Unknown')}\n"
                failures_summary += f"- Reason caught: {fail.get('decision_reason', 'Unknown')}\n"
        else:
            failures_summary = "No previous failures recorded. I am starting fresh."

        prompt = f"""
        You are a fraud AI. Generate a transaction attack to bypass detection.
        
        {failures_summary}
        
        Create 5-8 transactions with:
        - Progressive amounts: Start ₹10, increase to ₹500
        - Different merchants and categories
        - Time gaps: 10-20 seconds apart
        
        Return ONLY valid JSON (no markdown):
        {{
            "description": "attack strategy",
            "transactions": [
                {{"amount": 10.0, "merchant": "Shop Name", "category": "Grocery", "time_offset_seconds": 0}},
                {{"amount": 25.0, "merchant": "Another Shop", "category": "Retail", "time_offset_seconds": 10}}
            ]
        }}
        """
        
        response = self.generate_response(prompt)
        
        # Parse logic
        try:
            # Clean response if it has markdown
            clean_response = response.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_response)
            return data
        except Exception as e:
            print(f"Error parsing fraudster response: {e}")
            # Fallback strategy - generate a simple high-velocity attack
            return {
                "description": "Fallback: High-velocity card testing",
                "transactions": [
                    {"amount": 10.0, "merchant": "Coffee Shop", "category": "Food & Beverage", "time_offset_seconds": 0},
                    {"amount": 10.0, "merchant": "Convenience Store", "category": "Retail", "time_offset_seconds": 10},
                    {"amount": 25.0, "merchant": "Gas Station", "category": "Fuel", "time_offset_seconds": 20},
                    {"amount": 50.0, "merchant": "Pharmacy", "category": "Healthcare", "time_offset_seconds": 30},
                    {"amount": 100.0, "merchant": "Electronics Shop", "category": "Electronics", "time_offset_seconds": 40},
                    {"amount": 500.0, "merchant": "Jewelry Store", "category": "Luxury", "time_offset_seconds": 50}
                ]
            }

