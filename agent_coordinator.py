"""
Agent Coordinator - Orchestrates multi-agent discussion and decision making
"""
from datetime import datetime
from typing import Dict, List
from colorama import Fore, Style, init
from agents.risk_analyst import RiskAnalystAgent
from agents.pattern_detective import PatternDetectiveAgent
from agents.decision_maker import DecisionMakerAgent
from models import Transaction, FraudDecision

# Initialize colorama for colored console output
init(autoreset=True)


class AgentCoordinator:
    """Coordinates multiple AI agents for fraud detection"""
    
    def __init__(self):
        """Initialize all agents"""
        self.risk_analyst = RiskAnalystAgent()
        self.pattern_detective = PatternDetectiveAgent()
        self.decision_maker = DecisionMakerAgent()
        self.discussion_log = []
    
    def analyze_transaction(self, transaction: Transaction) -> FraudDecision:
        """
        Coordinate multi-agent analysis of a transaction
        
        Args:
            transaction: Transaction to analyze
            
        Returns:
            FraudDecision with complete analysis
        """
        self.discussion_log = []
        tx_dict = transaction.to_dict()
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🔍 MULTI-AGENT FRAUD ANALYSIS")
        print(f"{Fore.CYAN}Transaction ID: {transaction.transaction_id}")
        print(f"{Fore.CYAN}Amount: {transaction.currency} {transaction.amount:,.2f}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        # Step 1: Risk Analyst analyzes the transaction
        print(f"{Fore.RED}🔴 RISK ANALYST analyzing...{Style.RESET_ALL}")
        risk_analysis = self.risk_analyst.analyze(tx_dict)
        self._log_analysis("Risk Analyst", risk_analysis)
        
        # Step 2: Pattern Detective analyzes the transaction
        print(f"\n{Fore.GREEN}🟢 PATTERN DETECTIVE analyzing...{Style.RESET_ALL}")
        pattern_analysis = self.pattern_detective.analyze(tx_dict)
        self._log_analysis("Pattern Detective", pattern_analysis)
        
        # Step 3: Decision Maker synthesizes and decides
        print(f"\n{Fore.BLUE}🔵 DECISION MAKER synthesizing...{Style.RESET_ALL}")
        context = {
            'risk_analyst': risk_analysis,
            'pattern_detective': pattern_analysis
        }
        final_decision = self.decision_maker.analyze(tx_dict, context)
        self._log_analysis("Decision Maker", final_decision)
        
        # Create FraudDecision object
        decision = FraudDecision(
            transaction_id=transaction.transaction_id,
            final_score=final_decision.get('final_score', 50),
            decision=final_decision.get('decision', 'REVIEW'),
            risk_analyst_score=risk_analysis.get('score', 50),
            pattern_detective_score=pattern_analysis.get('score', 50),
            decision_maker_reasoning=final_decision.get('reasoning', ''),
            agent_discussion=self.discussion_log,
            timestamp=datetime.now().isoformat()
        )
        
        # Print final decision
        self._print_final_decision(decision)
        
        return decision
    
    def _log_analysis(self, agent_name: str, analysis: Dict):
        """Log agent analysis to discussion log"""
        self.discussion_log.append({
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        })
        
        # Print analysis summary
        score = analysis.get('score') or analysis.get('final_score', 'N/A')
        confidence = analysis.get('confidence', 'N/A')
        
        print(f"  Score: {score}/100")
        print(f"  Confidence: {confidence}%")
        
        # Print key findings or reasoning
        if 'key_findings' in analysis:
            print(f"  Key Findings:")
            for finding in analysis['key_findings'][:3]:  # Show top 3
                print(f"    • {finding}")
        
        if 'reasoning' in analysis:
            # Print first 150 chars of reasoning
            reasoning = analysis['reasoning']
            if len(reasoning) > 150:
                reasoning = reasoning[:150] + "..."
            print(f"  Reasoning: {reasoning}")
    
    def _print_final_decision(self, decision: FraudDecision):
        """Print formatted final decision"""
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}⚖️  FINAL DECISION")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        
        # Color code based on decision
        decision_color = Fore.GREEN if decision.decision == 'APPROVE' else (
            Fore.YELLOW if decision.decision == 'REVIEW' else Fore.RED
        )
        
        print(f"{decision_color}Decision: {decision.decision}{Style.RESET_ALL}")
        print(f"Final Score: {decision.final_score:.1f}/100")
        print(f"Risk Analyst Score: {decision.risk_analyst_score:.1f}/100")
        print(f"Pattern Detective Score: {decision.pattern_detective_score:.1f}/100")
        print(f"\n{Fore.CYAN}Reasoning:{Style.RESET_ALL}")
        print(f"{decision.decision_maker_reasoning[:300]}...")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
    
    def get_discussion_summary(self) -> List[Dict]:
        """Get the complete discussion log"""
        return self.discussion_log
