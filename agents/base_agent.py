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
        self.model = "qwen2.5:0.5b"
    
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
    
    def reset_history(self):
        """Clear conversation history"""
        self.conversation_history = []
