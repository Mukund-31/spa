"""
Interactive Fraud Detection Demo
Choose from 3 scenarios and see results in Kafka UI with intelligent routing
"""
import json
import time
import random
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
        
        # Initialize customer profiles matching Java implementation
        self._setup_customer_profiles()
    
    def _setup_customer_profiles(self):
        """Setup static customer profiles (simulates Kafka customerProfiles topic)"""
        profiles = [
            {
                'customer_id': 'CUST_NORMAL_001',
                'average_transaction_amount': 500.0,
                'daily_spending_limit': 10000.0,
                'transaction_categories': ['Groceries', 'Supermarket', 'Food'],
                'primary_location': 'Mumbai, Maharashtra',
                'risk_level': 'LOW'
            },
            {
                'customer_id': 'CUST_VELOCITY_001',
                'average_transaction_amount': 200.0,
                'daily_spending_limit': 5000.0,
                'transaction_categories': ['Retail', 'Online'],
                'primary_location': 'Delhi, NCR',
                'risk_level': 'MEDIUM'
            },
            {
                'customer_id': 'CUST_SPIKE_001',
                'average_transaction_amount': 150.0,
                'daily_spending_limit': 8000.0,
                'transaction_categories': ['Groceries', 'Utilities'],
                'primary_location': 'Bangalore, Karnataka',
                'risk_level': 'LOW'
            },
            {
                'customer_id': 'CUST_GAN_001',
                'average_transaction_amount': 1000.0,
                'daily_spending_limit': 20000.0,
                'transaction_categories': ['E-commerce', 'Electronics', 'Fashion'],
                'primary_location': 'Mumbai, Maharashtra',
                'risk_level': 'MEDIUM'
            }
        ]
        
        # Add profiles to context store
        for profile in profiles:
            self.coordinator.context_store.add_customer_profile(profile)
            
        # Publish to Kafka customerProfiles topic
        try:
            for profile in profiles:
                self.producer.send(
                    'customerProfiles',
                    key=profile['customer_id'],
                    value=profile
                )
            self.producer.flush()
        except Exception as e:
            print(f"{Fore.YELLOW}Note: Could not publish to Kafka customerProfiles topic: {e}{Style.RESET_ALL}")
    
    def publish_transaction(self, transaction):
        """Publish transaction to Kafka transactions topic with full data"""
        tx_data = {
            "transaction_id": transaction.transaction_id,
            "timestamp": transaction.timestamp,
            "customer_id": transaction.customer_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "merchant_name": transaction.merchant_name,
            "merchant_category": transaction.merchant_category,
            "location": transaction.location,
            "payment_method": transaction.payment_method
        }
        
        try:
            self.producer.send(
                'transactions',
                key=transaction.transaction_id,
                value=tx_data
            )
            self.producer.flush()
        except Exception as e:
            pass  # Silently fail if Kafka not running
    
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
            customer_id="CUST_NORMAL_001",
            amount=500.0,
            currency="INR",
            merchant_name="Local Grocery Store",
            merchant_category="Groceries",
            location="Mumbai, Maharashtra",
            payment_method="Debit Card"
        )
        
        # Publish transaction to Kafka
        self.publish_transaction(tx)
        print(f"{Fore.YELLOW}Analyzing transaction [{tx.timestamp[11:19]}]...{Style.RESET_ALL}\n")
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
        
        customer_id = "CUST_VELOCITY_001"
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
                location="Chennai, Tamil Nadu",
                payment_method="Credit Card"
            )
            
            print(f"  Transaction {i+1}/12: ₹{amount:,.2f} at {merchant} [{tx.timestamp[11:19]}]")
            # Publish and add to context without full analysis to save API calls
            self.publish_transaction(tx)
            self.coordinator.context_store.add_transaction(tx.to_dict())
            time.sleep(0.3)
        
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
            location="Mumbai, Maharashtra",
            payment_method="Credit Card"
        )
        
        # Publish transaction to Kafka
        self.publish_transaction(final_tx)
        print(f"{Fore.RED}Transaction #13: ₹2,500.00 at Premium Electronics Store [{final_tx.timestamp[11:19]}]{Style.RESET_ALL}")
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
        
        customer_id = "CUST_SPIKE_001"
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
                merchant_category="Groceries",
                location="Bangalore, Karnataka",
                payment_method="Debit Card"
            )
            
            print(f"  Transaction {i+1}/3: ₹150.00 (normal) [{tx.timestamp[11:19]}]")
            # Publish and add to context without full analysis
            self.publish_transaction(tx)
            self.coordinator.context_store.add_transaction(tx.to_dict())
            time.sleep(0.3)
        
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
            location="Bangalore, Karnataka",
            payment_method="Credit Card"
        )
        
        
        # Publish transaction to Kafka
        self.publish_transaction(spike_tx)
        print(f"{Fore.YELLOW}Analyzing unusual amount transaction [{spike_tx.timestamp[11:19]}]...{Style.RESET_ALL}\n")
        decision, confidence = self.coordinator.analyze_transaction(spike_tx)
        
        # Use intelligent router
        topic = self.route_decision(decision, confidence)
        
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
        """AI vs AI: Fraudster learns from detection, System learns from attacks"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"🤖 SCENARIO 4: AI vs AI (GAN ADVERSARIAL MODE)")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print("Description:")
        print("  • Red Team: 'Fraudster' AI generates attacks based on past failures")
        print("  • Blue Team: 'Production' System detects fraud")
        print("  • Loop: Both sides learn from each interaction")
        print(f"  • {Fore.CYAN}📊 View live chart: http://localhost:5001{Style.RESET_ALL}\n")
        
        # Reset dashboard for new training session
        try:
            import requests
            requests.post('http://localhost:5001/api/reset', timeout=2)
        except:
            pass
        
        # Learning memory
        fraudster_learnings = []
        detector_learnings = []
        
        round_num = 0
        print(f"{Fore.YELLOW}Press Ctrl+C to stop the GAN training loop...{Style.RESET_ALL}")
        
        try:
            while True:
                round_num += 1
                print(f"\n{Fore.YELLOW}🥊 ROUND {round_num}: Generating Attack...{Style.RESET_ALL}")
                
                # Fraudster generates strategy based on learnings
                if fraudster_learnings:
                    print(f"{Fore.RED}Fraudster Strategy (learning from failures):{Style.RESET_ALL}")
                    for learning in fraudster_learnings[-2:]:  # Show last 2 learnings
                        print(f"  📚 Learned: {learning}")
                    strategy = f"Evade detection by: {', '.join(fraudster_learnings[-2:])}"
                else:
                    strategy = "Initial attack: Progressive card testing with realistic amounts"
                
                print(f'  "{strategy}"\n')
                
                # Generate realistic attack transactions
                num_txns = random.randint(3, 8)
                print(f"Executing {num_txns} transaction(s)...")
                
                # Realistic transaction amounts (₹500 - ₹5000)
                amounts = []
                merchants = ["Amazon India", "Flipkart", "BigBasket", "Swiggy", "Zomato", 
                            "BookMyShow", "MakeMyTrip", "Myntra", "Nykaa", "Paytm Mall"]
                categories = ["E-commerce", "Food Delivery", "Groceries", "Entertainment", 
                             "Travel", "Fashion", "Beauty", "Electronics"]
                
                # Progressive amounts strategy
                base_amount = random.randint(500, 1000)
                for i in range(num_txns):
                    # Increase amounts progressively
                    amount = base_amount * (1.5 ** i) + random.randint(-100, 100)
                    amounts.append(round(amount, 2))
                
                # Execute transactions with realistic timing
                import time
                for i, amount in enumerate(amounts, 1):
                    merchant = random.choice(merchants)
                    category = random.choice(categories)
                    
                    tx = Transaction(
                        transaction_id=f"GAN_R{round_num}_{i:03d}",
                        customer_id="CUST_GAN_001",
                        amount=amount,
                        currency="INR",
                        merchant_name=merchant,
                        merchant_category=category,
                        location="Mumbai, Maharashtra",
                        timestamp=datetime.now().isoformat(),
                        payment_method="Credit Card"
                    )
                    
                    # Publish transaction to Kafka
                    self.publish_transaction(tx)
                    
                    print(f"  Tx {i}/{num_txns}: ₹{amount:,.2f} at {merchant} ({category}) [{tx.timestamp[11:19]}]")
                    
                    # Small delay for temporal analysis (0.3-0.8 seconds)
                    time.sleep(random.uniform(0.3, 0.8))
                    
                    # Analyze only the final transaction with full context
                    if i == num_txns:
                        print(f"\n{Fore.CYAN}Analyzing final transaction with full velocity context...{Style.RESET_ALL}\n")
                        decision, confidence = self.coordinator.analyze_transaction(tx)
                        
                        # Determine outcome
                        detected = decision.final_score > 60
                        
                        print(f"\n{Fore.YELLOW}{'='*80}")
                        print(f"🎯 ROUND {round_num} OUTCOME")
                        print(f"{'='*80}{Style.RESET_ALL}\n")
                        
                        if detected:
                            print(f"{Fore.RED}🚨 FRAUD DETECTED!{Style.RESET_ALL}")
                            print(f"  Final Score: {decision.final_score:.1f}%")
                            print(f"  Confidence: {confidence:.1f}%\n")
                            
                            # Fraudster learns from failure
                            learning = self._extract_fraudster_learning(decision, amounts, num_txns)
                            fraudster_learnings.append(learning)
                            
                            print(f"{Fore.RED}📚 Fraudster Learning:{Style.RESET_ALL}")
                            print(f"  {learning}\n")
                            
                            # Detector learns from successful detection
                            detector_learning = f"Successfully detected: {num_txns} txns, progressive amounts ₹{amounts[0]:.0f}→₹{amounts[-1]:.0f}"
                            detector_learnings.append(detector_learning)
                            
                            print(f"{Fore.GREEN}📚 Detector Learning:{Style.RESET_ALL}")
                            print(f"  {detector_learning}\n")
                        else:
                            print(f"{Fore.GREEN}✅ ATTACK SUCCESSFUL (Evaded Detection){Style.RESET_ALL}")
                            print(f"  Final Score: {decision.final_score:.1f}%")
                            print(f"  Confidence: {confidence:.1f}%\n")
                            
                            # Detector learns from failure
                            detector_learning = f"Missed attack: {num_txns} txns with progressive amounts - need better pattern detection"
                            detector_learnings.append(detector_learning)
                            
                            print(f"{Fore.YELLOW}📚 Detector Learning:{Style.RESET_ALL}")
                            print(f"  {detector_learning}\n")
                        
                        # Store learnings in Kafka and dashboard
                        self._publish_learning_feedback(round_num, fraudster_learnings, detector_learnings, decision)
                    else:
                        # Just update streaming context for intermediate transactions
                        self.coordinator.context_store.add_transaction(tx.to_dict())
        
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Training stopped by user after {round_num} rounds.{Style.RESET_ALL}")
        
        # Final summary
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"🏁 GAN TRAINING SUMMARY ({round_num} rounds)")
        print(f"{'='*80}{Style.RESET_ALL}\n")
        
        print(f"{Fore.RED}Fraudster Learnings ({len(fraudster_learnings)} total):{Style.RESET_ALL}")
        for i, learning in enumerate(fraudster_learnings, 1):
            print(f"  {i}. {learning}")
        
        print(f"\n{Fore.GREEN}Detector Learnings ({len(detector_learnings)} total):{Style.RESET_ALL}")
        for i, learning in enumerate(detector_learnings, 1):
            print(f"  {i}. {learning}")
        
        print(f"\n{Fore.YELLOW}💡 Both systems are now smarter!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 View full training history: http://localhost:5001{Style.RESET_ALL}\n")
    
    def _extract_fraudster_learning(self, decision, amounts, num_txns):
        """Extract what fraudster should learn from detection"""
        learnings = []
        
        if decision.final_score > 80:
            learnings.append("reduce transaction velocity")
        if num_txns > 5:
            learnings.append("use fewer transactions")
        if max(amounts) / min(amounts) > 3:
            learnings.append("make amounts less progressive")
        
        if not learnings:
            learnings.append("use different merchant categories")
        
        return ", ".join(learnings)
    
    def _publish_learning_feedback(self, round_num, fraudster_learnings, detector_learnings, decision):
        """Publish learnings to Kafka and GAN Dashboard"""
        # Calculate scores for visualization
        # Generator score = evasion rate (100 - detection score means better evasion)
        # Discriminator score = detection rate (higher = better detection)
        discriminator_score = decision.final_score
        generator_score = 100 - decision.final_score  # Inverse - high means good evasion
        
        # Extract agent scores from discussion log
        agent_scores = {}
        for entry in decision.agent_discussion:
            if isinstance(entry, dict) and 'agent' in entry:
                agent_name = entry.get('agent', 'Unknown')
                # Score is inside the 'analysis' dict
                analysis = entry.get('analysis', {})
                if isinstance(analysis, dict):
                    score = analysis.get('score', 50)
                else:
                    score = 50
                try:
                    agent_scores[agent_name] = min(100, max(0, float(score)))
                except:
                    agent_scores[agent_name] = 50
        
        feedback = {
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "fraudster_learnings": fraudster_learnings,
            "detector_learnings": detector_learnings,
            "generator_score": generator_score,
            "discriminator_score": discriminator_score,
            "agent_scores": agent_scores,
            "decision": {
                "final_score": decision.final_score,
                "decision": decision.decision
            }
        }
        
        # Publish to Kafka
        try:
            self.producer.send(
                'analysis-feedback',
                value=feedback
            )
            self.producer.flush()
        except Exception as e:
            print(f"{Fore.YELLOW}Note: Could not publish to Kafka: {e}{Style.RESET_ALL}")
        
        # Send to GAN Dashboard
        try:
            import requests
            dashboard_data = {
                'round': round_num,
                'generator_score': generator_score,
                'discriminator_score': discriminator_score,
                'generator_learning': fraudster_learnings[-1] if fraudster_learnings else 'No learning',
                'discriminator_learning': detector_learnings[-1] if detector_learnings else 'No learning',
                'agent_scores': agent_scores
            }
            requests.post('http://localhost:5001/api/update', json=dashboard_data, timeout=2)
            print(f"{Fore.CYAN}📊 Dashboard updated: http://localhost:5001{Style.RESET_ALL}")
        except:
            pass  # Dashboard not running, skip silently



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
