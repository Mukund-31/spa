"""
Test script for multi-agent fraud detection system
"""
from datetime import datetime
from colorama import Fore, Style, init
from models import Transaction
from agent_coordinator import AgentCoordinator

# Initialize colorama
init(autoreset=True)


def test_multi_agent_system():
    """Test the multi-agent fraud detection system"""
    
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}🧪 TESTING MULTI-AGENT FRAUD DETECTION SYSTEM")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}\n")
    
    # Create agent coordinator
    coordinator = AgentCoordinator()
    
    # Test Case 1: Suspicious transaction
    print(f"{Fore.YELLOW}TEST CASE 1: Suspicious Transaction{Style.RESET_ALL}")
    suspicious_tx = Transaction(
        transaction_id="TEST001",
        timestamp=datetime.now().isoformat(),
        customer_id="CUST1234",
        amount=45000.00,
        currency="USD",
        merchant_name="Unknown Wire Service",
        merchant_category="Wire Transfer",
        location="Nigeria",
        payment_method="Credit Card"
    )
    
    decision1 = coordinator.analyze_transaction(suspicious_tx)
    
    # Test Case 2: Legitimate transaction
    print(f"\n{Fore.YELLOW}TEST CASE 2: Legitimate Transaction{Style.RESET_ALL}")
    legitimate_tx = Transaction(
        transaction_id="TEST002",
        timestamp=datetime.now().isoformat(),
        customer_id="CUST5678",
        amount=45.99,
        currency="USD",
        merchant_name="Whole Foods Market",
        merchant_category="Grocery",
        location="United States",
        payment_method="Debit Card"
    )
    
    decision2 = coordinator.analyze_transaction(legitimate_tx)
    
    # Test Case 3: Medium risk transaction
    print(f"\n{Fore.YELLOW}TEST CASE 3: Medium Risk Transaction{Style.RESET_ALL}")
    medium_tx = Transaction(
        transaction_id="TEST003",
        timestamp=datetime.now().isoformat(),
        customer_id="CUST9999",
        amount=1500.00,
        currency="USD",
        merchant_name="Electronics Store",
        merchant_category="Retail",
        location="China",
        payment_method="Credit Card"
    )
    
    decision3 = coordinator.analyze_transaction(medium_tx)
    
    # Summary
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{Fore.MAGENTA}📋 TEST SUMMARY")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"\nTest 1 (Suspicious): Score={decision1.final_score:.1f}, Decision={decision1.decision}")
    print(f"Test 2 (Legitimate): Score={decision2.final_score:.1f}, Decision={decision2.decision}")
    print(f"Test 3 (Medium Risk): Score={decision3.final_score:.1f}, Decision={decision3.decision}")
    print(f"\n{Fore.GREEN}✓ All tests completed successfully!{Style.RESET_ALL}\n")


if __name__ == '__main__':
    test_multi_agent_system()
