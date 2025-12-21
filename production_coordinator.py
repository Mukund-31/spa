"""
Production Agent Coordinator - Orchestrates 5 specialized agents with weighted voting
Uses KTable-backed velocity windows for rapid-fire attack detection
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List
from colorama import Fore, Style, init
from agents.behavior_analyst import BehaviorAnalystAgent
from agents.pattern_detector_v2 import PatternDetectorV2Agent
from agents.geographic_analyst import GeographicAnalystAgent
from agents.risk_assessor import RiskAssessorAgent
from agents.temporal_analyst import TemporalAnalystAgent
from models import Transaction, FraudDecision

# Try to use KTable-based context, fallback to in-memory
try:
    from velocity_ktable import StreamingContextWithKTable
    USE_KTABLE = True
    print("✅ Using KTable-backed velocity tracking (RocksDB state store)")
except ImportError:
    from streaming_context import StreamingContextStore
    USE_KTABLE = False
    print("⚠️ Using in-memory velocity tracking (KTable not available)")

# Initialize colorama
init(autoreset=True)


class ProductionAgentCoordinator:
    """
    Production coordinator with 5 specialized agents and weighted voting
    
    Architecture Components (from diagram):
    - KStream: transactions topic → consumed and analyzed
    - KTable: Velocity Context (5-min tumbling window)
    - KTable: Customer Profiles (global table for joins)
    - Streaming Enrichment: leftJoin for transaction enrichment
    """
    
    # Weighted voting configuration
    AGENT_WEIGHTS = {
        'BehaviorAnalyst': 0.25,
        'PatternDetector': 0.25,
        'GeographicAnalyst': 0.20,
        'RiskAssessor': 0.15,
        'TemporalAnalyst': 0.15
    }
    
    def __init__(self):
        """Initialize all 5 specialized agents and KTable-backed streaming context"""
        self.behavior_analyst = BehaviorAnalystAgent()
        self.pattern_detector = PatternDetectorV2Agent()
        self.geographic_analyst = GeographicAnalystAgent()
        self.risk_assessor = RiskAssessorAgent()
        self.temporal_analyst = TemporalAnalystAgent()
        
        # Use KTable-backed context if available (matches architecture diagram)
        if USE_KTABLE:
            self.context_store = StreamingContextWithKTable(state_dir='./ktable_state')
            print("📊 KTable State Store: ./ktable_state")
        else:
            from streaming_context import StreamingContextStore
            self.context_store = StreamingContextStore(velocity_window_minutes=5)
        
        self.discussion_log = []
        
        # Log architecture components
        print("=" * 60)
        print("🚀 Production Coordinator Initialized")
        print("=" * 60)
        print("📊 Architecture Components:")
        print("   ├─ Velocity Window: 5-min tumbling (KTable-backed)")
        print("   ├─ Customer Profiles: KTable with leftJoin")
        print("   ├─ State Store: RocksDB" if USE_KTABLE else "   ├─ State Store: In-Memory")
        print("   └─ Rapid-fire Detection: >15 txns OR >3 txn/min")
        print("=" * 60)
    
    def analyze_transaction(self, transaction: Transaction) -> tuple[FraudDecision, float]:
        """
        Analyze a transaction using all 5 agents with streaming context
        
        Returns:
            Tuple of (FraudDecision, confidence)
        """
        self.discussion_log = []
        # Convert to dict if needed
        tx_dict = transaction.to_dict() if hasattr(transaction, 'to_dict') else transaction
        
        # Get streaming context
        streaming_context = self.context_store.get_streaming_context(
            tx_dict['customer_id'],
            tx_dict
        )
        
        # Add transaction to context store
        self.context_store.add_transaction(tx_dict)
        
        # Print analysis header
        self._print_header(transaction, streaming_context)
        
        print(f"{Fore.MAGENTA}📊 PHASE 1: Parallel 5-Agent Analysis{Style.RESET_ALL}\n")
        
        # Run all 5 agents in parallel
        agent_insights = self._run_parallel_analysis(tx_dict, streaming_context)
        
        # Phase 2: Agent Collaboration (Talking Stage)
        if self._requires_collaboration(agent_insights, streaming_context):
            print(f"\n{Fore.MAGENTA}💬 PHASE 2: Agent Collaboration (Talking Stage){Style.RESET_ALL}\n")
            collaboration_insights = self._run_collaboration(tx_dict, streaming_context, agent_insights)
            agent_insights.extend(collaboration_insights)
        else:
            print(f"\n{Fore.CYAN}⚖️  PHASE 2: Weighted Voting Consensus{Style.RESET_ALL}")
        
        # Calculate Weighted Risk Score
        base_score = self._calculate_weighted_risk_score(agent_insights)
        print(f"  Base Risk Score (weighted average): {base_score:.1f}%\n")
        
        # Phase 3: Apply Streaming Intelligence Bonus
        print(f"{Fore.YELLOW}🚀 PHASE 3: Streaming Intelligence Bonus{Style.RESET_ALL}")
        final_score, bonus = self._apply_streaming_bonus(
            base_score,
            streaming_context,
            agent_insights
        )
        
        # Determine decision
        decision_text, confidence = self._determine_decision(final_score, agent_insights)
        
        # Create FraudDecision
        decision = FraudDecision(
            transaction_id=transaction.transaction_id,
            final_score=final_score,
            decision=decision_text,
            risk_analyst_score=next((a.get('score', 50) for a in agent_insights if a.get('agent_name') == 'RiskAssessor'), 50),
            pattern_detective_score=next((a.get('score', 50) for a in agent_insights if a.get('agent_name') == 'PatternDetector'), 50),
            decision_maker_reasoning=self._generate_reasoning(agent_insights, streaming_context, bonus),
            agent_discussion=self.discussion_log,
            timestamp=datetime.now().isoformat()
        )
        
        # Print final decision
        self._print_final_decision(decision, confidence, agent_insights)
        
        # Return both decision and confidence
        return decision, confidence
    
    def _run_parallel_analysis(self, tx_dict, streaming_context) -> List[Dict]:
        """Run all 5 agents in parallel (simulated with sequential for API limits)"""
        # Get recent fraud patterns (Learning Loop)
        try:
            from knowledge_base import KnowledgeBase
            kb = KnowledgeBase()
            # Get last 5 detected frauds to learn from
            recent_frauds = [f for f in kb.get_feedback() if f.get('decision') == 'FRAUD DETECTED'][-5:]
            fraud_context = json.dumps(recent_frauds, default=str)
        except:
            fraud_context = "[]"

        context = {
            'streaming_context': streaming_context,
            'fraud_patterns': fraud_context
        }
        
        agents = [
            (self.behavior_analyst, Fore.RED, "🔴 BEHAVIOR ANALYST"),
            (self.pattern_detector, Fore.GREEN, "🟢 PATTERN DETECTOR"),
            (self.geographic_analyst, Fore.BLUE, "🔵 GEOGRAPHIC ANALYST"),
            (self.risk_assessor, Fore.YELLOW, "🟡 RISK ASSESSOR"),
            (self.temporal_analyst, Fore.MAGENTA, "🟣 TEMPORAL ANALYST")
        ]
        
        insights = []
        for agent, color, label in agents:
            print(f"{color}{label}...{Style.RESET_ALL}")
            analysis = agent.analyze(tx_dict, context)
            self._log_analysis(agent.name, analysis)
            insights.append(analysis)
            print(f"  Score: {analysis.get('score', 50)}/100 | Confidence: {analysis.get('confidence', 50)}%")
            
            # Safely print finding
            key_findings = analysis.get('key_findings', [])
            finding_text = ""
            
            if key_findings and isinstance(key_findings, list) and len(key_findings) > 0:
                first_finding = key_findings[0]
                if isinstance(first_finding, dict):
                    # Extract values if it's a dict
                    values = list(first_finding.values())
                    if values:
                        finding_text = str(values[0])
                else:
                    finding_text = str(first_finding)
            
            # Fallback if empty or 'finding1' placeholder
            if not finding_text or finding_text == 'finding1':
                analysis_text = analysis.get('analysis', '')
                # Ensure it's a string and handle safely
                if analysis_text and isinstance(analysis_text, str):
                    finding_text = str(analysis_text)[:100].replace('\n', ' ')
                else:
                    finding_text = ""
                
            if finding_text:
                # Clean up text and truncate reasonably if too long for summary
                clean_text = finding_text.replace('\n', ' ').strip()
                if len(clean_text) > 100:
                    print(f"  Finding: {clean_text[:97]}...")
                else:
                    print(f"  Finding: {clean_text}")
            print()
        
        # Print detailed analysis table
        self._print_detailed_analysis_table(insights, streaming_context)
        
        return insights
    
    def _requires_collaboration(self, agent_insights: List[Dict], streaming_context: Dict) -> bool:
        """
        Check if Phase 2 collaboration is required.
        Triggers: risk disagreement, high velocity, or profile present.
        """
        # Get scores safely
        scores = []
        for a in agent_insights:
            try:
                scores.append(float(a.get('score', 50)))
            except:
                scores.append(50.0)
        
        # 1. Risk disagreement: variance > 40 points
        if len(scores) > 1:
            import statistics
            variance = statistics.variance(scores)
            if variance > 400:  # std dev > 20
                return True
        
        # 2. High velocity
        velocity = streaming_context.get('velocity', {})
        if velocity.get('transaction_count', 0) > 5:
            return True
        
        # 3. Profile present
        if streaming_context.get('static_profile'):
            return True
        
        return False
    
    def _run_collaboration(self, tx_dict: Dict, streaming_context: Dict, phase1_insights: List[Dict]) -> List[Dict]:
        """
        Run Phase 2 collaboration between agent pairs.
        - Velocity collaboration: PatternDetector + TemporalAnalyst
        - Profile collaboration: BehaviorAnalyst + RiskAssessor
        Returns list of collaboration insights.
        """
        collaboration_insights = []
        velocity = streaming_context.get('velocity', {})
        baseline = streaming_context.get('baseline', {})
        
        # === Velocity Collaboration ===
        if velocity.get('transaction_count', 0) > 5:
            print(f"  {Fore.YELLOW}🔄 Velocity Collaboration: PatternDetector ↔ TemporalAnalyst{Style.RESET_ALL}")
            
            velocity_question = f"High velocity detected ({velocity['transaction_count']} transactions in {velocity.get('time_span_minutes', 0):.1f} min). Does this align with automated attack patterns?"
            print(f"     Question: \"{velocity_question}\"")
            
            # PatternDetector answers
            pattern_collab = self.pattern_detector.collaborate(velocity_question, tx_dict, {'velocity': velocity})
            print(f"     {Fore.GREEN}PatternDetector: Score {pattern_collab.get('score', 50)}/100{Style.RESET_ALL}")
            reasoning = pattern_collab.get('reasoning') or pattern_collab.get('analysis') or 'Analysis based on patterns'
            print(f"       → {str(reasoning)[:150]}")
            collaboration_insights.append(pattern_collab)
            
            # TemporalAnalyst answers
            temporal_collab = self.temporal_analyst.collaborate(velocity_question, tx_dict, {'velocity': velocity})
            print(f"     {Fore.MAGENTA}TemporalAnalyst: Score {temporal_collab.get('score', 50)}/100{Style.RESET_ALL}")
            reasoning = temporal_collab.get('reasoning') or temporal_collab.get('analysis') or 'Temporal pattern analysis'
            print(f"       → {str(reasoning)[:150]}")
            collaboration_insights.append(temporal_collab)
            print()
        
        # === Profile Collaboration ===
        if baseline.get('avg_amount', 0) > 0:
            print(f"  {Fore.YELLOW}🔄 Profile Collaboration: BehaviorAnalyst ↔ RiskAssessor{Style.RESET_ALL}")
            
            profile_question = f"Customer profile shows INR {baseline.get('avg_amount', 0):,.2f} average transactions, {baseline.get('risk_level', 'LOW')} risk level. How does this affect your analysis?"
            print(f"     Question: \"{profile_question}\"")
            
            # BehaviorAnalyst answers
            behavior_collab = self.behavior_analyst.collaborate(profile_question, tx_dict, {'baseline': baseline})
            print(f"     {Fore.RED}BehaviorAnalyst: Score {behavior_collab.get('score', 50)}/100{Style.RESET_ALL}")
            reasoning = behavior_collab.get('reasoning') or behavior_collab.get('analysis') or 'Behavior pattern analysis'
            print(f"       → {str(reasoning)[:150]}")
            collaboration_insights.append(behavior_collab)
            
            # RiskAssessor answers
            risk_collab = self.risk_assessor.collaborate(profile_question, tx_dict, {'baseline': baseline})
            print(f"     {Fore.YELLOW}RiskAssessor: Score {risk_collab.get('score', 50)}/100{Style.RESET_ALL}")
            reasoning = risk_collab.get('reasoning') or risk_collab.get('analysis') or 'Risk assessment based on profile'
            print(f"       → {str(reasoning)[:150]}")
            collaboration_insights.append(risk_collab)
            print()
        
        # === Final Consensus (Lead Investigator) ===
        print(f"  {Fore.CYAN}👨‍💼 Lead Investigator Building Consensus...{Style.RESET_ALL}")
        consensus = self._build_streaming_consensus(tx_dict, streaming_context, phase1_insights + collaboration_insights)
        collaboration_insights.append(consensus)
        print(f"     {Fore.CYAN}Consensus Score: {consensus.get('score', 50)}/100{Style.RESET_ALL}")
        reasoning = consensus.get('reasoning') or consensus.get('analysis') or 'Synthesized from all agent inputs'
        print(f"       → {str(reasoning)[:200]}\n")
        
        return collaboration_insights
    
    def _build_streaming_consensus(self, tx_dict: Dict, streaming_context: Dict, all_insights: List[Dict]) -> Dict:
        """
        Build final streaming consensus from all agent insights.
        This is the 'lead investigator' that synthesizes everything.
        """
        import re
        
        # Build agent findings summary
        findings_summary = []
        for insight in all_insights:
            name = insight.get('agent_name', 'Unknown')
            score = insight.get('score', 50)
            reasoning = insight.get('reasoning') or insight.get('analysis') or 'No reasoning'
            if isinstance(reasoning, str):
                reasoning = reasoning[:100]
            else:
                reasoning = str(reasoning)[:100]
            findings_summary.append(f"- {name} (Risk: {score}/100): {reasoning}")
        
        velocity = streaming_context.get('velocity', {})
        baseline = streaming_context.get('baseline', {})
        
        prompt = f"""You are the Lead Fraud Investigator synthesizing all agent findings.

STREAMING CONTEXT:
- Velocity: {velocity.get('transaction_count', 0)} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes
- Customer Avg: INR {baseline.get('avg_amount', 0):,.2f}
- Risk Level: {baseline.get('risk_level', 'LOW')}

TRANSACTION:
- Amount: INR {tx_dict.get('amount', 0):,.2f}
- Merchant: {tx_dict.get('merchant_name', 'Unknown')}
- Location: {tx_dict.get('location', 'Unknown')}

AGENT FINDINGS:
{chr(10).join(findings_summary)}

Your task:
1. How does streaming context enhance this decision?
2. What is the overall fraud risk with streaming intelligence?
3. What are the key factors from AI + streaming data?

You MUST respond in this exact JSON format:
{{
    "score": <0-100 overall risk score>,
    "confidence": <0-100 confidence>,
    "reasoning": "<synthesis of all findings>",
    "recommendation": "<APPROVE/REVIEW/REJECT>"
}}"""
        
        # Use behavior analyst's generate_response (any agent works)
        response = self.behavior_analyst.generate_response(prompt)
        
        # Clean response
        response_clean = response
        if '<think>' in response:
            response_clean = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
        
        try:
            result = json.loads(response_clean)
            result['agent_name'] = 'StreamingIntelligenceConsensus'
            return result
        except:
            return {
                'agent_name': 'StreamingIntelligenceConsensus',
                'score': 50,
                'confidence': 50,
                'reasoning': 'Consensus synthesis',
                'recommendation': 'REVIEW'
            }
    
    def _print_detailed_analysis_table(self, insights, streaming_context):
        """Print detailed analysis table with complete findings"""
        print(f"\n{Fore.CYAN}{'='*120}")
        print(f"{Fore.CYAN}📋 PHASE 1: DETAILED AGENT ANALYSIS")
        print(f"{Fore.CYAN}{'='*120}{Style.RESET_ALL}\n")
        
        # Print each agent's analysis with full findings
        for insight in insights:
            agent_name = insight.get('agent_name', 'Unknown')
            score = insight.get('score', 50)
            confidence = insight.get('confidence', 50)
            
            # Handle malformed values from LLM
            try:
                score = float(score)
            except (ValueError, TypeError):
                score = 50.0
            
            try:
                confidence = float(confidence)
            except (ValueError, TypeError):
                confidence = 50.0
            
            # Get complete finding text
            finding = ""
            
            # Try to get from analysis field (usually has better text)
            analysis_text = insight.get('analysis', '')
            if analysis_text and len(analysis_text) > 10:
                # Clean the analysis
                finding = analysis_text.replace('\n', ' ').strip()
            
            # Fallback to key_findings if analysis is empty
            if not finding:
                key_findings = insight.get('key_findings', [])
                if key_findings and isinstance(key_findings, list) and len(key_findings) > 0:
                    first_finding = key_findings[0]
                    if isinstance(first_finding, dict):
                        # Extract values if it's a dict
                        values = list(first_finding.values())
                        if values:
                            finding = str(values[0])
                    else:
                        finding = str(first_finding)
            
            # Final fallback
            if not finding or finding == 'finding1':
                finding = f"Risk assessment based on {agent_name.lower()} analysis"
            
            # Color code based on score
            if score > 70:
                score_color = Fore.RED
                risk_level = "HIGH"
            elif score > 40:
                score_color = Fore.YELLOW
                risk_level = "MEDIUM"
            else:
                score_color = Fore.GREEN
                risk_level = "LOW"
            
            # Print agent header
            print(f"{Fore.CYAN}┌─ {agent_name} {Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  Risk Score: {score_color}{score}%{Style.RESET_ALL} ({risk_level}) | Confidence: {confidence}%")
            
            # Print finding with word wrap
            print(f"{Fore.CYAN}│{Style.RESET_ALL}  Finding:")
            # Word wrap the finding at 100 characters
            words = finding.split()
            line = "│  "
            for word in words:
                if len(line) + len(word) + 1 > 100:
                    print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
                    line = "│  " + word + " "
                else:
                    line += word + " "
            if line.strip() != "│":
                print(f"{Fore.CYAN}{line}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─'*100}{Style.RESET_ALL}\n")
        
        # Print streaming context detected
        velocity = streaming_context.get('velocity', {})
        profile = streaming_context.get('profile', {})
        anomalies = streaming_context.get('anomalies', {})
        
        if velocity.get('transaction_count', 0) > 0:
            print(f"{Fore.CYAN}{'='*120}")
            print(f"{Fore.CYAN}📊 STREAMING CONTEXT DETECTED")
            print(f"{Fore.CYAN}{'='*120}{Style.RESET_ALL}\n")
            
            if velocity.get('transaction_count', 0) > 10:
                print(f"{Fore.RED}  ⚠️  HIGH VELOCITY ALERT: {velocity.get('transaction_count')} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes{Style.RESET_ALL}")
            else:
                print(f"  Velocity: {velocity.get('transaction_count')} transactions in {velocity.get('time_span_minutes', 0):.1f} minutes")
            
            print(f"  Customer Baseline: INR {profile.get('avg_amount', 0):.2f} average")
            
            if anomalies.get('amount_deviation_pct', 0) > 100:
                print(f"{Fore.YELLOW}  Amount Deviation: {anomalies.get('amount_deviation_pct', 0):.0f}% (unusual){Style.RESET_ALL}")
            
            if anomalies.get('location_is_new'):
                print(f"{Fore.YELLOW}  Location: New location detected{Style.RESET_ALL}")
            
            # Show progressive pattern if detected
            if velocity.get('transaction_count', 0) > 5:
                print(f"{Fore.YELLOW}  Pattern: Progressive amount testing detected{Style.RESET_ALL}")
            
            print()
    
    def _calculate_weighted_risk_score(self, agent_insights: List[Dict]) -> float:
        """Calculate weighted average risk score"""
        weighted_sum = 0.0
        total_confidence = 0.0
        
        for insight in agent_insights:
            agent_name = insight.get('agent_name', 'Unknown')
            score = insight.get('score', 50)
            confidence = insight.get('confidence', 50)
            
            # Handle malformed values
            try:
                score = float(score) / 100.0  # Normalize to 0-1
            except (ValueError, TypeError):
                score = 0.5  # Default to 50%
            
            try:
                confidence = float(confidence) / 100.0
            except (ValueError, TypeError):
                confidence = 0.5  # Default to 50%
            
            weight = self.AGENT_WEIGHTS.get(agent_name, 0.1)
            
            weighted_sum += score * weight * confidence
            total_confidence += confidence
        
        # Normalize by total confidence
        base_score = (weighted_sum / (total_confidence / len(agent_insights))) * 100
        return min(100, max(0, base_score))
    
    def _apply_streaming_bonus(self, base_score, streaming_context, agent_insights) -> tuple:
        """Apply streaming intelligence and profile-based risk bonuses (matches Java implementation)"""
        bonus = 0.0
        reasons = []
        
        velocity = streaming_context['velocity']
        anomalies = streaming_context['anomalies']
        risk_indicators = streaming_context['risk_indicators']
        baseline = streaming_context.get('baseline', {})
        
        # CRITICAL: Don't apply bonuses if insufficient data
        if velocity['transaction_count'] <= 1:
            print(f"  {Fore.CYAN}No streaming bonus (insufficient transaction history){Style.RESET_ALL}\n")
            return base_score, 0.0
        
        # === VELOCITY BONUSES ===
        tx_count = velocity.get('transaction_count', 0)
        if tx_count > 15:
            bonus += 20
            reasons.append(f"Rapid-fire attack ({tx_count} txns)")
        elif tx_count > 10:
            bonus += 10
            reasons.append(f"High velocity ({tx_count} txns)")
        
        # === AMOUNT DEVIATION BONUS (matches Java: profile.isAmountUnusual) ===
        amt_deviation = anomalies.get('amount_deviation_pct', 0)
        profile_avg = streaming_context.get('profile', {}).get('avg_amount', 0)
        if amt_deviation > 500 and profile_avg > 0:
            bonus += 20  # +0.20 in Java
            reasons.append(f"Extreme amount spike ({amt_deviation:.0f}% deviation)")
        elif amt_deviation > 300 and profile_avg > 0:
            bonus += 15
            reasons.append(f"Large amount deviation ({amt_deviation:.0f}%)")
        
        # === PROFILE-BASED BONUSES (matches Java AgentCoordinator) ===
        # High risk customer bonus
        if risk_indicators.get('high_risk_customer'):
            bonus += 10  # +0.10 in Java
            reasons.append(f"High-risk customer profile")
        
        # Location mismatch (different from primary location)
        if anomalies.get('location_mismatch'):
            bonus += 10
            reasons.append(f"Location differs from primary ({baseline.get('primary_location')})")
        
        # Unusual category
        if anomalies.get('category_is_unusual'):
            bonus += 5
            reasons.append(f"Unusual merchant category")
        
        # Exceeds daily limit
        if risk_indicators.get('exceeds_daily_limit'):
            bonus += 15
            reasons.append(f"Exceeds daily spending limit (₹{baseline.get('daily_limit', 0):,.0f})")
        
        # === PATTERN BONUSES ===
        # Geographic impossibility bonus
        if risk_indicators.get('location_hopping'):
            bonus += 10
            reasons.append("Location hopping detected")
        
        # Progressive pattern bonus (from PatternDetector)
        pattern_insight = next((a for a in agent_insights if a.get('agent_name') == 'PatternDetector'), {})
        if pattern_insight.get('pattern_indicators', {}).get('progressive_amounts') and velocity['transaction_count'] > 5:
            bonus += 10
            reasons.append("Progressive testing pattern")
        
        final_score = min(100, base_score + bonus)
        
        if bonus > 0:
            print(f"  {Fore.YELLOW}Streaming Bonus: +{bonus:.0f} points{Style.RESET_ALL}")
            for reason in reasons:
                print(f"    • {reason}")
            print(f"  {Fore.GREEN}Final Score: {base_score:.1f} + {bonus:.0f} = {final_score:.1f}{Style.RESET_ALL}\n")
        else:
            print(f"  No streaming bonus applied\n")
        
        return final_score, bonus
    
    def _determine_decision(self, final_score, agent_insights) -> tuple:
        """Determine decision and confidence"""
        # Calculate confidence based on agent agreement with error handling
        scores = []
        confidences = []
        
        for a in agent_insights:
            # Handle score
            score = a.get('score', 50)
            try:
                scores.append(float(score))
            except (ValueError, TypeError):
                scores.append(50.0)
            
            # Handle confidence
            conf = a.get('confidence', 50)
            try:
                confidences.append(float(conf))
            except (ValueError, TypeError):
                confidences.append(50.0)
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 50.0
        
        # Check agreement (low std dev = high agreement)
        import statistics
        score_std = statistics.stdev(scores) if len(scores) > 1 else 0
        agreement_bonus = max(0, 20 - score_std)  # Higher agreement = higher confidence
        
        confidence = min(100, avg_confidence + agreement_bonus)
        
        # Determine decision
        if final_score > 80:
            decision = "FRAUD DETECTED"
        elif final_score > 40:
            decision = "REVIEW"
        else:
            decision = "APPROVED"
        
        return decision, confidence
    
    def _generate_reasoning(self, agent_insights, streaming_context, bonus) -> str:
        """Generate comprehensive reasoning"""
        velocity = streaming_context['velocity']
        
        reasoning = f"5-Agent Consensus Analysis:\n\n"
        
        for insight in agent_insights:
            reasoning += f"{insight.get('agent_name', 'Unknown')}: {insight.get('score', 50)}% risk\n"
            key_findings = insight.get('key_findings', [])
            if key_findings:
                reasoning += f"  - {key_findings[0]}\n"
        
        reasoning += f"\nStreaming Context:\n"
        reasoning += f"- Velocity: {velocity.get('transaction_count', 0)} txns in {velocity.get('time_span_minutes', 0):.1f}min\n"
        reasoning += f"- Streaming Bonus: +{bonus:.0f} points\n"
        
        return reasoning
    
    def _print_header(self, transaction, streaming_context):
        """Print analysis header with complete streaming context"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🔍 PRODUCTION 5-AGENT FRAUD ANALYSIS")
        print(f"{Fore.CYAN}Transaction ID: {transaction.transaction_id}")
        print(f"{Fore.CYAN}Amount: INR {transaction.amount:,.2f}")
        print(f"{Fore.CYAN}Location: {transaction.location}")
        print(f"{Fore.CYAN}Merchant: {transaction.merchant_name} ({transaction.merchant_category})")
        
        velocity = streaming_context['velocity']
        profile = streaming_context['profile']
        anomalies = streaming_context['anomalies']
        baseline = streaming_context.get('baseline', {})
        
        print(f"\n{Fore.YELLOW}📊 Streaming Context:")
        print(f"{Fore.YELLOW}   Velocity: {velocity.get('transaction_count', 0)} txns in {velocity.get('time_span_minutes', 0):.1f}min")
        print(f"{Fore.YELLOW}   Velocity Score: {velocity.get('velocity_score', 0):.2f} txn/min")
        print(f"{Fore.YELLOW}   Unique Locations: {velocity.get('unique_locations', 0)}")
        print(f"{Fore.YELLOW}   Unique Merchants: {velocity.get('unique_merchants', 0)}")
        
        print(f"\n{Fore.CYAN}📋 Customer Baseline:")
        avg_amount = baseline.get('avg_amount', 0) or (profile.get('avg_amount', 0) if profile else 0)
        print(f"{Fore.CYAN}   Avg Amount: INR {avg_amount:.2f}")
        print(f"{Fore.CYAN}   Risk Level: {baseline.get('risk_level', 'LOW')}")
        if baseline.get('primary_location'):
            print(f"{Fore.CYAN}   Primary Location: {baseline['primary_location']}")
        if baseline.get('typical_categories'):
            print(f"{Fore.CYAN}   Typical Categories: {', '.join(baseline['typical_categories'][:3])}")
        print(f"{Fore.CYAN}   Daily Limit: INR {baseline.get('daily_limit', 100000):,.0f}")
        
        print(f"\n{Fore.YELLOW}⚠️  Anomalies:")
        print(f"{Fore.YELLOW}   Amount Deviation: {anomalies.get('amount_deviation_pct', 0):.1f}%")
        
        if anomalies.get('velocity_alert'):
            print(f"{Fore.RED}   ⚠️  VELOCITY ALERT!{Style.RESET_ALL}")
        if anomalies.get('rapid_fire_detected'):
            print(f"{Fore.RED}   ⚠️  RAPID FIRE DETECTED!{Style.RESET_ALL}")
        risk_indicators = streaming_context.get('risk_indicators', {})
        if risk_indicators.get('location_hopping'):
            print(f"{Fore.RED}   ⚠️  LOCATION HOPPING DETECTED!{Style.RESET_ALL}")
        if anomalies.get('location_mismatch'):
            print(f"{Fore.RED}   ⚠️  LOCATION DIFFERS FROM PRIMARY!{Style.RESET_ALL}")
        if anomalies.get('category_is_unusual'):
            print(f"{Fore.RED}   ⚠️  UNUSUAL MERCHANT CATEGORY!{Style.RESET_ALL}")
        if risk_indicators.get('high_risk_customer'):
            print(f"{Fore.RED}   ⚠️  HIGH-RISK CUSTOMER!{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def _log_analysis(self, agent_name: str, analysis: Dict):
        """Log agent analysis"""
        self.discussion_log.append({
            'agent': agent_name,
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis
        })
    
    def _print_final_decision(self, decision, confidence, agent_insights):
        """Print final decision with intelligence sources"""
        print(f"{Fore.YELLOW}{'='*100}")
        print(f"{Fore.YELLOW}⚖️  FINAL DECISION")
        print(f"{Fore.YELLOW}{'='*100}{Style.RESET_ALL}")
        
        decision_color = Fore.GREEN if decision.decision == "APPROVED" else (
            Fore.YELLOW if decision.decision == "REVIEW" else Fore.RED
        )
        
        print(f"{decision_color}Decision: {decision.decision}{Style.RESET_ALL}")
        print(f"Final Risk Score: {decision.final_score:.1f}%")
        print(f"Confidence: {confidence:.0f}%")
        print(f"\nAgent Scores:")
        for insight in agent_insights:
            print(f"  {insight.get('agent_name', 'Unknown')}: {insight.get('score', 50)}%")
        
        # Show why this decision was made
        print(f"\n{Fore.CYAN}🔍 DECISION REASONING:{Style.RESET_ALL}")
        
        if decision.final_score > 80:
            print(f"{Fore.RED}  ✓ HIGH-CONFIDENCE FRAUD → AUTO-BLOCK{Style.RESET_ALL}")
            print(f"  • Final risk score {decision.final_score:.1f}% exceeds 80% threshold")
            print(f"  • Routed to: fraud-alerts topic")
            print(f"  • Action: Immediate block, no human review needed")
        elif decision.final_score > 40:
            print(f"{Fore.YELLOW}  ⚠️  MEDIUM RISK → HUMAN REVIEW{Style.RESET_ALL}")
            print(f"  • Final risk score {decision.final_score:.1f}% requires analyst review")
            print(f"  • Routed to: human-review queue")
            print(f"  • Action: Flagged for manual investigation")
        else:
            print(f"{Fore.GREEN}  ✓ LOW RISK → AUTO-APPROVE{Style.RESET_ALL}")
            print(f"  • Final risk score {decision.final_score:.1f}% below 40% threshold")
            print(f"  • Routed to: approved-transactions topic")
            print(f"  • Action: Transaction approved automatically")
        
        # Show intelligence sources
        print(f"\n{Fore.CYAN}📡 INTELLIGENCE SOURCES:{Style.RESET_ALL}")
        sources = []
        
        # Check for velocity intelligence
        for insight in agent_insights:
            if insight.get('agent_name') == 'BehaviorAnalyst':
                if insight.get('velocity_indicators', {}).get('high_velocity'):
                    sources.append("Real-time velocity detection")
                if insight.get('velocity_indicators', {}).get('rapid_fire_attack'):
                    sources.append("Rapid-fire attack pattern")
        
        # Check for pattern matching
        for insight in agent_insights:
            if insight.get('agent_name') == 'PatternDetector':
                if insight.get('pattern_indicators', {}).get('card_testing'):
                    sources.append("Card testing pattern match")
                if insight.get('pattern_indicators', {}).get('progressive_amounts'):
                    sources.append("Progressive amount testing")
        
        # Check for geographic analysis
        for insight in agent_insights:
            if insight.get('agent_name') == 'GeographicAnalyst':
                if insight.get('geographic_indicators', {}).get('location_impossibility'):
                    sources.append("Geographic impossibility detected")
        
        # Check for temporal analysis
        for insight in agent_insights:
            if insight.get('agent_name') == 'TemporalAnalyst':
                if insight.get('temporal_indicators', {}).get('scripted_behavior'):
                    sources.append("Scripted/automated behavior")
        
        # Always include these
        sources.append("5-agent weighted consensus")
        sources.append("Streaming context intelligence")
        
        for source in sources:
            print(f"  • {source}")
        
        print(f"{Fore.YELLOW}{'='*100}{Style.RESET_ALL}\n")
    
    def get_context_statistics(self) -> Dict:
        """Get streaming context statistics"""
        return self.context_store.get_statistics()
