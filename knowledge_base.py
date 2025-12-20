"""
Knowledge Base - simulated File API for Ollama
Stores feedback and fraud patterns for agents to learn from
"""
import json
import os
from typing import Dict, List
from datetime import datetime

class KnowledgeBase:
    def __init__(self, storage_dir="brain/memory"):
        self.storage_dir = storage_dir
        self.fraud_patterns_file = os.path.join(storage_dir, "fraud_patterns.json")
        self.feedback_file = os.path.join(storage_dir, "analyst_feedback.json")
        self._ensure_storage()
        
    def _ensure_storage(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        for f in [self.fraud_patterns_file, self.feedback_file]:
            if not os.path.exists(f):
                with open(f, 'w') as file:
                    json.dump([], file)

    def add_feedback(self, feedback: Dict):
        """Store analyst feedback or verdict results"""
        history = self.get_feedback()
        feedback['stored_at'] = datetime.now().isoformat()
        history.append(feedback)
        # Keep last 50 entries to context limit
        if len(history) > 50:
            history = history[-50:]
        
        with open(self.feedback_file, 'w') as f:
            json.dump(history, f, indent=2)

    def get_feedback(self) -> List[Dict]:
        """Retrieve feedback history"""
        try:
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def log_fraud_pattern(self, pattern: Dict):
        """Log a detected fraud pattern (Detector knowledge)"""
        patterns = self.get_fraud_patterns()
        patterns.append(pattern)
        with open(self.fraud_patterns_file, 'w') as f:
            json.dump(patterns, f, indent=2)

    def get_fraud_patterns(self) -> List[Dict]:
        try:
            with open(self.fraud_patterns_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def get_recent_failures(self) -> List[Dict]:
        """Get recent fraud attempts that were CAUGHT (for Fraudster to learn what fails)"""
        feedback = self.get_feedback()
        # Return detected frauds
        return [f for f in feedback if f.get('decision') == 'FRAUD DETECTED']

    def get_recent_successes(self) -> List[Dict]:
        """Get recent fraud attempts that were APPROVED (Fraudster successes)"""
        # In a real system, we'd only know this if an analyst marked it later.
        # For the demo, we might store 'successful_evasion' if explicitly tagged.
        feedback = self.get_feedback()
        return [f for f in feedback if f.get('decision') == 'APPROVED' and f.get('was_actual_fraud', False)]
