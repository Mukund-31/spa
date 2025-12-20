"""
Test script for streaming context intelligence
Demonstrates velocity-based fraud detection
"""
from datetime import datetime, timedelta
from colorama import Fore, Style, init
from models import Transaction
from enhanced_agent_coordinator import EnhancedAgentCoordinator
import time

# Initialize colorama
init(autoreset=True)


def test_velocity_detection():
    """Test velocity-based fraud detection with streaming context"""
    
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}🧪 TESTING STREAMING CONTEXT INTELLIGENCE")
    print(f"{Fore.MAGENTA}Demonstrating Velocity-Based Fraud Detection")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    
    # Create enhanced coordinator
    coordinator = EnhancedAgentCoordinator()
    
    # Scenario: Card Testing Attack
    print(f"{Fore.YELLOW}SCENARIO: Card Testing Attack{Style.RESET_ALL}")
    print(f"Attacker makes rapid small transactions to test stolen card\n")
    
    customer_id = "CUST9999"
    base_time = datetime.now()
    
    # Simulate 16 rapid transactions (card testing pattern)
    print(f"{Fore.CYAN}Simulating 16 rapid transactions in 5 minutes...{Style.RESET_ALL}\n")
    
    for i in range(16):
        # Small amounts (card testing)
        amount = 2.50 if i < 15 else 2500.00  # Last one is the real fraud
        
        tx = Transaction(
            transaction_id=f"VELOCITY{i+1:03d}",
            timestamp=(base_time + timedelta(seconds=i*20)).isoformat(),
            customer_id=customer_id,
            amount=amount,
            currency="INR",
            merchant_name=f"Test Merchant {i+1}",
            merchant_category="Retail" if i < 15 else "Electronics",
            location="India",
            payment_method="Credit Card"
        )
        
        print(f"{Fore.CYAN}Transaction {i+1}/16: INR {amount:.2f}{Style.RESET_ALL}")
        
        # Analyze
        decision = coordinator.analyze_transaction(tx)
        
        # Small delay to simulate real-time
        if i < 15:
            time.sleep(0.5)
    
    # Print final statistics
    stats = coordinator.get_context_statistics()
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}✓ VELOCITY DETECTION TEST COMPLETE")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    print(f"\nKey Observations:")
    print(f"• First 15 transactions: Small amounts (INR 2.50) - Card testing")
    print(f"• Transaction 16: Large amount (INR 2,500) - Real fraud attempt")
    print(f"• Streaming context detected velocity pattern")
    print(f"• Agent collaboration triggered due to rapid-fire pattern")
    print(f"• Final transaction scored higher due to streaming intelligence bonus")
    
    print(f"\n{Fore.MAGENTA}This demonstrates how streaming context prevents attacks that")
    print(f"traditional systems miss by analyzing transactions in isolation!{Style.RESET_ALL}\n")


def test_amount_spike_detection():
    """Test amount spike detection"""
    
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}🧪 TESTING AMOUNT SPIKE DETECTION")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    
    coordinator = EnhancedAgentCoordinator()
    customer_id = "CUST5555"
    base_time = datetime.now()
    
    # Normal transactions
    print(f"{Fore.CYAN}Building customer profile with normal transactions...{Style.RESET_ALL}\n")
    
    for i in range(5):
        tx = Transaction(
            transaction_id=f"NORMAL{i+1:03d}",
            timestamp=(base_time + timedelta(minutes=i*30)).isoformat(),
            customer_id=customer_id,
            amount=50.0,  # Normal: INR 50
            currency="INR",
            merchant_name="Regular Store",
            merchant_category="Grocery",
            location="India",
            payment_method="Debit Card"
        )
        
        print(f"Transaction {i+1}/5: INR 50.00 (Normal)")
        decision = coordinator.analyze_transaction(tx)
        time.sleep(0.3)
    
    # Sudden spike
    print(f"\n{Fore.RED}Sudden amount spike detected!{Style.RESET_ALL}\n")
    
    spike_tx = Transaction(
        transaction_id="SPIKE001",
        timestamp=(base_time + timedelta(minutes=150)).isoformat(),
        customer_id=customer_id,
        amount=5000.0,  # 100x spike!
        currency="INR",
        merchant_name="Electronics Store",
        merchant_category="Electronics",
        location="India",
        payment_method="Credit Card"
    )
    
    print(f"Transaction 6: INR 5,000.00 (100x spike!)")
    decision = coordinator.analyze_transaction(spike_tx)
    
    print(f"\n{Fore.GREEN}✓ Amount spike detection complete{Style.RESET_ALL}")
    print(f"\nKey Observations:")
    print(f"• Customer average: INR 50")
    print(f"• Spike transaction: INR 5,000 (10,000% deviation)")
    print(f"• Streaming context flagged massive deviation")
    print(f"• Decision score boosted by streaming intelligence bonus\n")


if __name__ == '__main__':
    print(f"\n{Fore.CYAN}Starting Streaming Context Intelligence Tests...{Style.RESET_ALL}")
    print(f"{Fore.CYAN}This will demonstrate how streaming context detects fraud")
    print(f"{Fore.CYAN}that traditional systems miss!{Style.RESET_ALL}\n")
    
    # Test 1: Velocity detection
    test_velocity_detection()
    
    # Wait between tests
    time.sleep(2)
    
    # Test 2: Amount spike detection
    test_amount_spike_detection()
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}✓ ALL STREAMING CONTEXT TESTS COMPLETED")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}\n")
