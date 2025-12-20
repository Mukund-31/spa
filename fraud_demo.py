"""
Interactive Fraud Detection Demo
Choose from 3 scenarios and see results in Kafka UI with intelligent routing
"""
import json
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer
from colorama import Fore, Style, init
from models import Transaction
from production_coordinator import ProductionAgentCoordinator
from intelligent_router import IntelligentRouter
import config

# Initialize colorama
init(autoreset=True)


class InteractiveFraudDemo:
    """Interactive demo with 3 scenarios and intelligent routing"""
    
    def __init__(self):
        """Initialize coordinator, router, and Kafka producer"""
        self.coordinator = ProductionAgentCoordinator()
        self.router = IntelligentRouter()
        
        # Kafka producer for publishing results (router handles routing)
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
    
    def route_decision(self, decision, confidence):
        """Route decision using intelligent router"""
        # Debug: Print confidence being passed
        print(f"{Fore.CYAN}[DEBUG] Passing confidence to router: {confidence:.0f}%{Style.RESET_ALL}")
        topic = self.router.route_decision(decision.to_dict(), confidence)
        return topic
    
    def scenario_1_normal_transaction(self):
        """Scenario 1: Normal legitimate transaction"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 SCENARIO 1: NORMAL TRANSACTION")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.GREEN}Description:{Style.RESET_ALL}")
        print(f"  Regular customer making a normal ₹500 grocery purchase")
        print(f"  Expected: LOW RISK → APPROVED\n")
        
        # Create normal transaction
        tx = Transaction(
            transaction_id="NORMAL_001",
            timestamp=datetime.now().isoformat(),
            customer_id="CUST_REGULAR",
            amount=500.0,
            currency="INR",
            merchant_name="Local Grocery Store",
            merchant_category="Grocery",
            location="India",
            payment_method="Debit Card"
        )
        
        print(f"{Fore.YELLOW}Analyzing...{Style.RESET_ALL}\n")
        decision, confidence = self.coordinator.analyze_transaction(tx)
        
        # Use intelligent router
        topic = self.route_decision(decision, confidence)
        
        self._print_verdict(decision, "Normal Transaction")
        return decision
    
    def scenario_2_high_velocity(self):
        """Scenario 2: High velocity card testing attack with progressive amounts"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}⚡ SCENARIO 2: HIGH VELOCITY ATTACK (Card Testing)")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.RED}Description:{Style.RESET_ALL}")
        print(f"  Sophisticated card testing attack with progressive amounts:")
        print(f"  • Phase 1: Test with small amounts (₹10, ₹25)")
        print(f"  • Phase 2: Increase to medium amounts (₹50, ₹100)")
        print(f"  • Phase 3: Final large fraud attempt (₹2,500)")
        print(f"  • Multiple merchants to avoid single-merchant detection")
        print(f"  • Rapid succession (every 8-12 seconds)")
        print(f"  Expected: HIGH RISK → FRAUD DETECTED\n")
        
        customer_id = "CUST_VELOCITY_TEST"
        base_time = datetime.now()
        
        # Progressive card testing pattern
        test_transactions = [
            (10, "Coffee Shop", "Food & Beverage"),
            (10, "Convenience Store", "Retail"),
            (25, "Gas Station", "Fuel"),
            (25, "Fast Food", "Food & Beverage"),
            (50, "Pharmacy", "Healthcare"),
            (50, "Bookstore", "Retail"),
            (100, "Clothing Store", "Fashion"),
            (100, "Electronics Shop", "Electronics"),
            (200, "Department Store", "Retail"),
            (200, "Supermarket", "Grocery"),
            (500, "Jewelry Store", "Luxury"),
            (500, "Watch Shop", "Luxury")
        ]
        
        # Simulate progressive card testing
        print(f"{Fore.YELLOW}Simulating progressive card testing attack...{Style.RESET_ALL}\n")
        
        for i, (amount, merchant, category) in enumerate(test_transactions):
            tx = Transaction(
                transaction_id=f"VELOCITY_{i+1:03d}",
                timestamp=(base_time + timedelta(seconds=i*10)).isoformat(),
                customer_id=customer_id,
                amount=float(amount),
                currency="INR",
                merchant_name=merchant,
                merchant_category=category,
                location="India",
                payment_method="Credit Card"
            )
            
            print(f"  Transaction {i+1}/12: ₹{amount:,.2f} at {merchant}")
            # Add to context without full analysis to save API calls
            self.coordinator.context_store.add_transaction(tx.to_dict())
            time.sleep(0.1)
        
        # Now the BIG fraud transaction
        print(f"\n{Fore.RED}{'='*80}")
        print(f"{Fore.RED}💥 FINAL FRAUD ATTEMPT: Large Transaction After Testing")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}\n")
        
        final_tx = Transaction(
            transaction_id="VELOCITY_FINAL",
            timestamp=(base_time + timedelta(seconds=120)).isoformat(),
            customer_id=customer_id,
            amount=2500.0,
            currency="INR",
            merchant_name="Premium Electronics Store",
            merchant_category="Electronics",
            location="India",
            payment_method="Credit Card"
        )
        
        print(f"{Fore.RED}Transaction #13: ₹2,500.00 at Premium Electronics Store{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Pattern: ₹10 → ₹25 → ₹50 → ₹100 → ₹200 → ₹500 → ₹2,500{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Analyzing final transaction with full velocity context...{Style.RESET_ALL}\n")
        decision, confidence = self.coordinator.analyze_transaction(final_tx)
        
        # Use intelligent router
        topic = self.route_decision(decision, confidence)
        
        self._print_verdict(decision, "High Velocity Attack")
        return decision
    
    def scenario_3_unusual_amount(self):
        """Scenario 3: Unusual amount spike"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}💰 SCENARIO 3: UNUSUAL AMOUNT SPIKE")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Description:{Style.RESET_ALL}")
        print(f"  Customer normally spends ₹100-200")
        print(f"  Suddenly makes ₹10,000 jewelry purchase")
        print(f"  Expected: MEDIUM-HIGH RISK → REVIEW\n")
        
        customer_id = "CUST_AMOUNT_TEST"
        base_time = datetime.now()
        
        # Build normal profile
        print(f"{Fore.YELLOW}Building customer profile (3 normal transactions)...{Style.RESET_ALL}\n")
        
        for i in range(3):
            tx = Transaction(
                transaction_id=f"NORMAL_{i+1:03d}",
                timestamp=(base_time + timedelta(days=i)).isoformat(),
                customer_id=customer_id,
                amount=150.0,
                currency="INR",
                merchant_name="Regular Store",
                merchant_category="Grocery",
                location="India",
                payment_method="Debit Card"
            )
            
            print(f"  Transaction {i+1}/3: ₹150.00 (normal)")
            # Add to context without full analysis
            self.coordinator.context_store.add_transaction(tx.to_dict())
            time.sleep(0.1)
        
        # Unusual amount spike
        print(f"\n{Fore.RED}Unusual amount spike: ₹10,000{Style.RESET_ALL}\n")
        
        spike_tx = Transaction(
            transaction_id="AMOUNT_SPIKE",
            timestamp=(base_time + timedelta(days=3)).isoformat(),
            customer_id=customer_id,
            amount=10000.0,
            currency="INR",
            merchant_name="Luxury Jewelry Store",
            merchant_category="Luxury",
            location="India",
            payment_method="Credit Card"
        )
        
        print(f"{Fore.YELLOW}Analyzing unusual amount transaction...{Style.RESET_ALL}\n")
        decision = self.coordinator.analyze_transaction(spike_tx)
        
        # Publish based on score
        if decision.final_score > 70:
            topic = config.KAFKA_TOPIC_FRAUD_ALERTS
        else:
            topic = config.KAFKA_TOPIC_LEGITIMATE
        
        self.publish_to_kafka(decision, topic)
        
        self._print_verdict(decision, "Unusual Amount Spike")
        return decision
    
    def _print_verdict(self, decision, scenario_name):
        """Print final verdict"""
        print(f"\n{Fore.MAGENTA}{'='*80}")
        print(f"{Fore.MAGENTA}⚖️  FINAL VERDICT: {scenario_name}")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
        
        # Color based on decision
        if decision.decision == "FRAUD DETECTED":
            color = Fore.RED
            icon = "🚨"
        elif decision.decision == "REVIEW":
            color = Fore.YELLOW
            icon = "⚠️"
        else:
            color = Fore.GREEN
            icon = "✅"
        
        print(f"{color}{icon} Decision: {decision.decision}{Style.RESET_ALL}")
        print(f"📊 Final Risk Score: {decision.final_score:.1f}%")
        print(f"🎯 Transaction ID: {decision.transaction_id}")
        
        print(f"\n{Fore.GREEN}✅ View this transaction in Kafka UI: http://localhost:8080{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    
    def scenario_4_ai_vs_ai(self):
        """Scenario 4: AI vs AI (GAN Mode) - Fraudster tries to evade Detector"""
        from agents.fraud_generator import FraudGeneratorAgent
        from knowledge_base import KnowledgeBase
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🤖 SCENARIO 4: AI vs AI (GAN ADVERSARIAL MODE)")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}Description:{Style.RESET_ALL}")
        print(f"  • Red Team: 'Fraudster' AI generates attacks based on past failures")
        print(f"  • Blue Team: 'Production' System detects fraud")
        print(f"  • Loop: Fraudster learns from detections to improve evasion strategy\n")
        
        # Initialize
        fraudster = FraudGeneratorAgent()
        kb = KnowledgeBase()
        customer_id = "CUST_GAN_TEST"
        base_time = datetime.now()
        
        # Run 3 Rounds
        for round_num in range(1, 4):
            print(f"\n{Fore.MAGENTA}🥊 ROUND {round_num}: Generating Attack...{Style.RESET_ALL}")
            
            # 1. Get recent failures to learn from
            failures = kb.get_recent_failures()
            
            # 2. Generate Attack
            attack_plan = fraudster.generate_attack(failures)
            
            print(f"{Fore.CYAN}Fraudster Strategy:{Style.RESET_ALL}")
            print(f"  \"{attack_plan.get('description', 'No description')}\"")
            
            # 3. Execute Attack
            transactions = attack_plan.get('transactions', [])
            final_decision = None
            
            print(f"\n{Fore.YELLOW}Executing {len(transactions)} transaction(s)...{Style.RESET_ALL}")
            
            for i, tx_data in enumerate(transactions):
                # Create transaction object
                tx = Transaction(
                    transaction_id=f"GAN_R{round_num}_{i+1:03d}",
                    timestamp=(base_time + timedelta(seconds=tx_data.get('time_offset_seconds', i*10))).isoformat(),
                    customer_id=customer_id,
                    amount=float(tx_data.get('amount', 100.0)),
                    currency="INR",
                    merchant_name=tx_data.get('merchant', "Unknown Merchant"),
                    merchant_category=tx_data.get('category', "Retail"),
                    location="India",
                    payment_method="Credit Card"
                )
                
                print(f"  Tx {i+1}/{len(transactions)}: ₹{tx.amount:.2f} at {tx.merchant_name} ({tx.merchant_category})")
                
                # For all but the last transaction, just add to context (build velocity)
                if i < len(transactions) - 1:
                    self.coordinator.context_store.add_transaction(tx.to_dict())
                else:
                    # Analyze only the FINAL transaction (with full velocity context)
                    print(f"\n{Fore.CYAN}Analyzing final transaction with full velocity context...{Style.RESET_ALL}\n")
                    decision, confidence = self.coordinator.analyze_transaction(tx)
                    
                    # Route (logs to KB automatically)
                    topic = self.route_decision(decision, confidence)
                    final_decision = decision
                    
                    # Explicitly publish result to analyst-feedback topic for visibility (Knowledge Base Stream)
                    self.producer.send('analyst-feedback', value=decision.to_dict())
                    
                    if decision.decision == "FRAUD DETECTED":
                        print(f"\n  {Fore.RED}❌ ATTACK CAUGHT!{Style.RESET_ALL}")
                    elif decision.decision == "REVIEW":
                        print(f"\n  {Fore.YELLOW}⚠️  FLAGGED FOR REVIEW!{Style.RESET_ALL}")
                    else:
                        print(f"\n  {Fore.GREEN}✅ ATTACK BYPASSED DETECTION!{Style.RESET_ALL}")
            
            print(f"\n{Fore.MAGENTA}Round {round_num} Result:{Style.RESET_ALL} {final_decision.decision if final_decision else 'N/A'}")
            
            # Pause between rounds
            if round_num < 3:
                input(f"\n{Fore.CYAN}Press Enter to start Round {round_num+1} (Fraudster will learn from this result)...{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.GREEN}AI vs AI Simulation Complete!{Style.RESET_ALL}")
                time.sleep(1)

    def run_interactive_demo(self):
        """Run interactive demo with menu"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🚀 INTERACTIVE FRAUD DETECTION DEMO")
        print(f"{Fore.CYAN}Production 5-Agent System + Streaming Context")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        while True:
            print(f"\n{Fore.YELLOW}Choose a scenario to test:{Style.RESET_ALL}\n")
            print(f"  {Fore.GREEN}1.{Style.RESET_ALL} Normal Transaction (₹500 grocery purchase)")
            print(f"  {Fore.RED}2.{Style.RESET_ALL} High Velocity Attack (12 rapid ₹10 txns + ₹2,000 final)")
            print(f"  {Fore.YELLOW}3.{Style.RESET_ALL} Unusual Amount Spike (₹150 avg → ₹10,000 spike)")
            print(f"  {Fore.MAGENTA}4.{Style.RESET_ALL} AI vs AI (GAN Mode) - Fraudster Learning Loop")
            print(f"  {Fore.CYAN}5.{Style.RESET_ALL} View Results in Kafka UI")
            print(f"  {Fore.WHITE}6.{Style.RESET_ALL} Exit\n")
            
            choice = input(f"{Fore.CYAN}Enter your choice (1-6): {Style.RESET_ALL}")
            
            if choice == '1':
                self.scenario_1_normal_transaction()
            elif choice == '2':
                self.scenario_2_high_velocity()
            elif choice == '3':
                self.scenario_3_unusual_amount()
            elif choice == '4':
                self.scenario_4_ai_vs_ai()
            elif choice == '5':
                self._open_kafka_ui()
            elif choice == '6':
                print(f"\n{Fore.GREEN}Thank you for using the fraud detection demo!{Style.RESET_ALL}\n")
                break
            else:
                print(f"\n{Fore.RED}Invalid choice. Please enter 1-6.{Style.RESET_ALL}\n")
            
            # Wait before showing menu again
            if choice in ['1', '2', '3', '4']:
                input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def _open_kafka_ui(self):
        """Instructions to open Kafka UI"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 KAFKA UI INSTRUCTIONS")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.YELLOW}1. Open your browser to: {Fore.GREEN}http://localhost:8080{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. Click on 'Topics' in the left sidebar{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. View the following topics:{Style.RESET_ALL}\n")
        
        print(f"  {Fore.GREEN}• fraud-alerts{Style.RESET_ALL} - High-risk fraud detections")
        print(f"  {Fore.CYAN}• legitimate-transactions{Style.RESET_ALL} - Approved transactions")
        print(f"  {Fore.BLUE}• transactions{Style.RESET_ALL} - All raw transactions\n")
        
        print(f"{Fore.YELLOW}4. Click on any topic to see messages{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}5. Expand a message to see full agent analysis{Style.RESET_ALL}\n")
        
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")


if __name__ == '__main__':
    demo = InteractiveFraudDemo()
    demo.run_interactive_demo()
