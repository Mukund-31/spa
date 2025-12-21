"""
Base Agent - Abstract base class for all fraud detection agents
Now using Ollama for local AI inference
"""
from abc import ABC, abstractmethod
from typing import Dict
import requests
import json


class BaseAgent(ABC):
    """Abstract base class for all AI agents using Ollama"""
    
    def __init__(self, name: str, role: str, expertise: str):
        """
        Initialize base agent with Ollama
        
        Args:
            name: Agent name
            role: Agent role
            expertise: Agent expertise description
        """
        self.name = name
        self.role = role
        self.expertise = expertise
        self.conversation_history = []
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "deepseek-r1:1.5b"  # Reasoning model, better at following logical rules
    
    def get_system_prompt(self) -> str:
        """Get system prompt for this agent"""
        return f"""You are {self.name}, a {self.role}.

Your expertise: {self.expertise}

Your responsibilities:
{self.get_responsibilities()}

Be thorough but concise. Focus on your area of expertise."""
    
    @abstractmethod
    def get_responsibilities(self) -> str:
        """Get agent-specific responsibilities"""
        pass
    
    @abstractmethod
    def analyze(self, transaction: dict, context: dict = None) -> Dict:
        """
        Analyze a transaction
        
        Args:
            transaction: Transaction data
            context: Additional context (e.g., other agents' analyses)
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate response using Ollama
        
        Args:
            prompt: The prompt to send to Ollama
            
        Returns:
            Generated response text
        """
        try:
            # Prepare request for Ollama
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"  # Request JSON format
            }
            
            # Call Ollama API with increased timeout
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=120  # Increased from 30 to 120 seconds for complex prompts
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def collaborate(self, question: str, transaction: dict, context: dict = None) -> Dict:
        """
        Collaborate with peer agents by answering a discussion question.
        Used in Phase 2 collaboration stage.
        
        Args:
            question: The collaboration question from coordinator
            transaction: Transaction data
            context: Additional context
            
        Returns:
            Dictionary with collaboration response (score, reasoning, recommendation)
        """
        import re
        
        prompt = f"""You are {self.name}, a {self.role} fraud detection specialist.

COLLABORATION QUESTION:
{question}

TRANSACTION DETAILS:
- Amount: INR {transaction.get('amount', 0):,.2f}
- Merchant: {transaction.get('merchant_name', 'Unknown')} ({transaction.get('merchant_category', 'Unknown')})
- Location: {transaction.get('location', 'Unknown')}
- Payment Method: {transaction.get('payment_method', 'Unknown')}

{f"CONTEXT: {json.dumps(context, default=str)}" if context else ""}

Based on your expertise in {self.expertise}, analyze this situation and provide your assessment.
IMPORTANT: You MUST include a detailed "reasoning" field explaining WHY you gave this score.

Respond in this exact JSON format:
{{
    "score": <0-100 risk score>,
    "confidence": <0-100 confidence percentage>,
    "reasoning": "<REQUIRED: 2-3 sentences explaining your score based on {self.expertise}>",
    "recommendation": "<APPROVE/REVIEW/REJECT>"
}}"""
        
        response = self.generate_response(prompt)
        
        # Clean response
        response_clean = response
        if '<think>' in response:
            response_clean = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        
        try:
            result = json.loads(response_clean)
            result['agent_name'] = f"{self.name}-collaboration"
            # Ensure reasoning exists
            if not result.get('reasoning'):
                result['reasoning'] = f"Analysis based on {self.expertise}"
            return result
        except:
            return {
                'agent_name': f"{self.name}-collaboration",
                'score': 50,
                'confidence': 50,
                'reasoning': response_clean[:200] if response_clean else f"Collaboration analysis by {self.name}",
                'recommendation': 'REVIEW'
            }
    
    def reset_history(self):
        """Clear conversation history"""
        self.conversation_history = []
