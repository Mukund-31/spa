"""
Transaction Producer - Generates realistic transaction data and publishes to Kafka
"""
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
from faker import Faker
from colorama import Fore, Style, init
import config
from models import Transaction

# Initialize colorama and Faker
init(autoreset=True)
fake = Faker()


class TransactionProducer:
    """Generates and publishes transactions to Kafka"""
    
    def __init__(self):
        """Initialize Kafka producer"""
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        self.transaction_count = 0
        
    def generate_transaction(self, suspicious: bool = False) -> Transaction:
        """
        Generate a realistic transaction
        
        Args:
            suspicious: Whether to generate a suspicious transaction
            
        Returns:
            Transaction object
        """
        if suspicious:
            # Generate suspicious transaction
            amount = random.choice([
                random.uniform(5000, 50000),  # Large amount
                random.uniform(0.01, 1.0),    # Micro transaction
            ])
            merchant_category = random.choice([
                'Wire Transfer', 'Cryptocurrency', 'Money Transfer',
                'Gambling', 'Adult Entertainment', 'Unknown'
            ])
            location = random.choice([
                'Nigeria', 'Russia', 'Unknown', 'China', 'Romania'
            ])
            merchant_name = random.choice([
                'Unknown Merchant', 'Cash Advance', 'Wire Service',
                fake.company()
            ])
        else:
            # Generate legitimate transaction
            amount = random.uniform(5, 500)
            merchant_category = random.choice([
                'Grocery', 'Restaurant', 'Gas Station', 'Retail',
                'Entertainment', 'Healthcare', 'Utilities', 'Transportation'
            ])
            location = random.choice([
                'United States', 'Canada', 'United Kingdom', 'Germany',
                'France', 'Australia', 'Japan'
            ])
            merchant_name = fake.company()
        
        transaction = Transaction(
            transaction_id=f"TXN{self.transaction_count:06d}",
            timestamp=datetime.now().isoformat(),
            customer_id=f"CUST{random.randint(1000, 9999)}",
            amount=round(amount, 2),
            currency='INR',
            merchant_name=merchant_name,
            merchant_category=merchant_category,
            location=location,
            payment_method=random.choice(['Credit Card', 'Debit Card', 'Digital Wallet', 'Bank Transfer'])
        )
        
        self.transaction_count += 1
        return transaction
    
    def publish_transaction(self, transaction: Transaction):
        """
        Publish transaction to Kafka
        
        Args:
            transaction: Transaction to publish
        """
        try:
            future = self.producer.send(
                config.KAFKA_TOPIC_TRANSACTIONS,
                key=transaction.transaction_id,
                value=transaction.to_dict()
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            print(f"{Fore.GREEN}✓ Published: {transaction.transaction_id} | "
                  f"{transaction.currency} {transaction.amount:,.2f} | "
                  f"{transaction.merchant_category}{Style.RESET_ALL}")
            
        except KafkaError as e:
            print(f"{Fore.RED}✗ Error publishing transaction: {e}{Style.RESET_ALL}")
    
    def run(self, count: int = None, rate: float = None):
        """
        Run the producer
        
        Args:
            count: Number of transactions to generate (None for infinite)
            rate: Transactions per second (uses config default if None)
        """
        rate = rate or config.TRANSACTION_RATE
        delay = 1.0 / rate
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🚀 TRANSACTION PRODUCER STARTED")
        print(f"{Fore.CYAN}Rate: {rate} transactions/second")
        print(f"{Fore.CYAN}Topic: {config.KAFKA_TOPIC_TRANSACTIONS}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        try:
            iteration = 0
            while count is None or iteration < count:
                # Determine if this should be suspicious
                suspicious = random.random() < config.SUSPICIOUS_TRANSACTION_RATIO
                
                # Generate and publish transaction
                transaction = self.generate_transaction(suspicious)
                self.publish_transaction(transaction)
                
                iteration += 1
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Producer stopped by user{Style.RESET_ALL}")
        finally:
            self.producer.close()
            print(f"{Fore.CYAN}Total transactions published: {self.transaction_count}{Style.RESET_ALL}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Transaction Producer')
    parser.add_argument('--count', type=int, help='Number of transactions to generate')
    parser.add_argument('--rate', type=float, help='Transactions per second')
    
    args = parser.parse_args()
    
    producer = TransactionProducer()
    producer.run(count=args.count, rate=args.rate)
