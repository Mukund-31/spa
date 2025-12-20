"""
Enhanced Agent Coordinator with Streaming Context Intelligence
Implements adaptive collaboration based on velocity and disagreement
"""
from datetime import datetime
from typing import Dict, List
from colorama import Fore, Style, init
from agents.risk_analyst import RiskAnalystAgent
from agents.pattern_detective import PatternDetectiveAgent
from agents.decision_maker import DecisionMakerAgent
from models import Transaction, FraudDecision
from streaming_context import StreamingContextStore

# Initialize colorama for colored console output
init(autoreset=True)


class EnhancedAgentCoordinator:
    """Coordinates multiple AI agents with streaming context intelligence"""
    
    def __init__(self):
        """Initialize all agents and streaming context store"""
        self.risk_analyst = RiskAnalystAgent()
        self.pattern_detective = PatternDetectiveAgent()
        self.decision_maker = DecisionMakerAgent()
        self.discussion_log = []
        
        # Streaming context store
        self.context_store = StreamingContextStore(velocity_window_minutes=10)
    
    def analyze_transaction(self, transaction: Transaction) -> FraudDecision:
        """
        Coordinate multi-agent analysis with streaming context
        
        Args:
            transaction: Transaction to analyze
            
        Returns:
            FraudDecision with complete analysis
        """
        self.discussion_log = []
        tx_dict = transaction.to_dict()
        
        # Get streaming context
        streaming_context = self.context_store.get_streaming_context(
            transaction.customer_id,
            tx_dict
        )
        
        # Add transaction to context store
        self.context_store.add_transaction(tx_dict)
        
        # Print header with streaming context
        self._print_header(transaction, streaming_context)
        
        # Phase 1: Parallel Analysis with Streaming Context
        print(f"{Fore.MAGENTA}📊 PHASE 1: Parallel Streaming-Enhanced Analysis{Style.RESET_ALL}\n")
        
        risk_analysis = self._analyze_with_context(
            self.risk_analyst,
            tx_dict,
            streaming_context,
            Fore.RED,
            "🔴 RISK ANALYST"
        )
        
        pattern_analysis = self._analyze_with_context(
            self.pattern_detective,
            tx_dict,
            streaming_context,
            Fore.GREEN,
            "🟢 PATTERN DETECTIVE"
        )
        
        # Determine if agents should collaborate
        should_collaborate = self._should_agents_collaborate(
            risk_analysis,
            pattern_analysis,
            streaming_context
        )
        
        # Phase 2: Adaptive Collaboration (if needed)
        if should_collaborate:
            print(f"\n{Fore.YELLOW}⚠️  PHASE 2: Agent Collaboration Triggered{Style.RESET_ALL}")
            print(f"Reason: {should_collaborate['reason']}\n")
            
            # Agents discuss their findings
            collaboration_context = {
                'risk_analyst': risk_analysis,
                'pattern_detective': pattern_analysis,
                'streaming_context': streaming_context,
                'collaboration_reason': should_collaborate['reason']
            }
        else:
            print(f"\n{Fore.CYAN}✓ PHASE 2: Skipped (agents in agreement){Style.RESET_ALL}\n")
            collaboration_context = {
                'risk_analyst': risk_analysis,
                'pattern_detective': pattern_analysis,
                'streaming_context': streaming_context
            }
        
        # Phase 3: Final Decision with Streaming Intelligence Bonus
        print(f"{Fore.BLUE}🔵 PHASE 3: Decision Synthesis + Streaming Bonus{Style.RESET_ALL}")
        final_decision = self.decision_maker.analyze(tx_dict, collaboration_context)
        
        # Apply streaming intelligence bonus
        final_score = self._apply_streaming_bonus(
            final_decision.get('final_score', 50),
            streaming_context,
            risk_analysis,
            pattern_analysis
        )
        
        # Update decision
        decision_text = 'APPROVE' if final_score < 40 else ('REVIEW' if final_score < 70 else 'REJECT')
        
        self._log_analysis("Decision Maker", final_decision)
        
        # Create FraudDecision object
        decision = FraudDecision(
            transaction_id=transaction.transaction_id,
            final_score=final_score,
            decision=decision_text,
            risk_analyst_score=risk_analysis.get('score', 50),
            pattern_detective_score=pattern_analysis.get('score', 50),
            decision_maker_reasoning=final_decision.get('reasoning', '') + f"\n\nStreaming Context Applied: Velocity={streaming_context['velocity']['transaction_count']} txns in {streaming_context['velocity']['time_span_minutes']:.1f}min",
            agent_discussion=self.discussion_log,
            timestamp=datetime.now().isoformat()
        )
        
        # Print final decision
        self._print_final_decision(decision, streaming_context)
        
        return decision
    
    def _analyze_with_context(self, agent, tx_dict, streaming_context, color, label):
        """Analyze transaction with streaming context"""
        print(f"{color}{label} (with streaming context)...{Style.RESET_ALL}")
        
        # Pass streaming context as part of the context parameter
        context = {'streaming_context': streaming_context}
        
        analysis = agent.analyze(tx_dict, context)
        self._log_analysis(agent.name, analysis)
        
        return analysis
    
    def _should_agents_collaborate(self, risk_analysis, pattern_analysis, streaming_context):
        """
        Determine if agents should enter collaboration mode
        
        Returns:
            Dict with 'should_collaborate' and 'reason' or False
        """
        risk_score = risk_analysis.get('score', 50)
        pattern_score = pattern_analysis.get('score', 50)
        
        # High disagreement
        score_diff = abs(risk_score - pattern_score)
        if score_diff > 30:
            return {
                'should_collaborate': True,
                'reason': f'High disagreement (Δ{score_diff:.0f} points)'
            }
        
        # High velocity detected
        if streaming_context['anomalies']['velocity_alert']:
            return {
                'should_collaborate': True,
                'reason': f"Velocity alert ({streaming_context['velocity']['transaction_count']} txns)"
            }
        
        # Rapid fire attack
        if streaming_context['anomalies']['rapid_fire_detected']:
            return {
                'should_collaborate': True,
                'reason': 'Rapid-fire attack pattern detected'
            }
        
        # Location hopping
        if streaming_context['risk_indicators']['location_hopping']:
            return {
                'should_collaborate': True,
                'reason': 'Location hopping detected'
            }
        
        return False
    
    def _apply_streaming_bonus(self, base_score, streaming_context, risk_analysis, pattern_analysis):
        """Apply streaming intelligence bonus to final score"""
        bonus = 0
        
        # Velocity bonus
        if streaming_context['velocity']['transaction_count'] > 15:
            bonus += 20
        elif streaming_context['velocity']['transaction_count'] > 10:
            bonus += 10
        
        # Amount spike bonus
        if streaming_context['anomalies']['amount_deviation_pct'] > 500:
            bonus += 15
        elif streaming_context['anomalies']['amount_deviation_pct'] > 300:
            bonus += 10
        
        # Location hopping bonus
        if streaming_context['risk_indicators']['location_hopping']:
            bonus += 10
        
        # Merchant hopping bonus
        if streaming_context['risk_indicators']['merchant_hopping']:
            bonus += 10
        
        final_score = min(100, base_score + bonus)
        
        if bonus > 0:
            print(f"  {Fore.YELLOW}Streaming Bonus: +{bonus} points{Style.RESET_ALL}")
            print(f"  Final Score: {base_score} + {bonus} = {final_score}")
        
        return final_score
    
    def _print_header(self, transaction, streaming_context):
        """Print analysis header with streaming context"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🔍 MULTI-AGENT FRAUD ANALYSIS (Streaming-Enhanced)")
        print(f"{Fore.CYAN}Transaction ID: {transaction.transaction_id}")
        print(f"{Fore.CYAN}Amount: {transaction.currency} {transaction.amount:,.2f}")
        
        # Streaming context summary
        velocity = streaming_context['velocity']
        print(f"{Fore.YELLOW}📊 Streaming Context:")
        print(f"{Fore.YELLOW}   Velocity: {velocity['transaction_count']} txns in {velocity['time_span_minutes']:.1f}min")
        print(f"{Fore.YELLOW}   Customer Avg: {streaming_context['profile']['avg_amount']:.2f}")
        print(f"{Fore.YELLOW}   Deviation: {streaming_context['anomalies']['amount_deviation_pct']:.1f}%")
        
        if streaming_context['anomalies']['velocity_alert']:
            print(f"{Fore.RED}   ⚠️  VELOCITY ALERT!{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
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
            for finding in analysis['key_findings'][:2]:  # Show top 2
                print(f"    • {finding}")
    
    def _print_final_decision(self, decision: FraudDecision, streaming_context):
        """Print formatted final decision"""
        print(f"\n{Fore.YELLOW}{'='*80}")
        print(f"{Fore.YELLOW}⚖️  FINAL DECISION (Streaming-Enhanced)")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
        
        # Color code based on decision
        decision_color = Fore.GREEN if decision.decision == 'APPROVE' else (
            Fore.YELLOW if decision.decision == 'REVIEW' else Fore.RED
        )
        
        print(f"{decision_color}Decision: {decision.decision}{Style.RESET_ALL}")
        print(f"Final Score: {decision.final_score:.1f}/100")
        print(f"Risk Analyst: {decision.risk_analyst_score:.1f} | Pattern Detective: {decision.pattern_detective_score:.1f}")
        print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}\n")
    
    def get_discussion_summary(self) -> List[Dict]:
        """Get the complete discussion log"""
        return self.discussion_log
    
    def get_context_statistics(self) -> Dict:
        """Get streaming context statistics"""
        return self.context_store.get_statistics()
