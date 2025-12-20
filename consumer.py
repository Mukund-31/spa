"""
Fraud Detection Consumer - Consumes transactions and analyzes with AI agents
"""
import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from colorama import Fore, Style, init
import config
from models import Transaction, FraudDecision
from agent_coordinator import AgentCoordinator

# Initialize colorama
init(autoreset=True)


class FraudDetectionConsumer:
    """Consumes transactions and performs multi-agent fraud detection"""
    
    def __init__(self):
        """Initialize Kafka consumer, producer, and AI agents"""
        # Consumer for incoming transactions
        self.consumer = KafkaConsumer(
            config.KAFKA_TOPIC_TRANSACTIONS,
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='fraud-detection-group',
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        # Producer for results
        self.producer = KafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # AI Agent Coordinator
        self.agent_coordinator = AgentCoordinator()
        
        # Statistics
        self.processed_count = 0
        self.fraud_count = 0
        self.review_count = 0
        self.approved_count = 0
    
    def process_transaction(self, transaction_data: dict):
        """
        Process a transaction with multi-agent analysis
        
        Args:
            transaction_data: Transaction data dictionary
        """
        try:
            # Create Transaction object
            transaction = Transaction(**transaction_data)
            
            # Analyze with multi-agent system
            decision = self.agent_coordinator.analyze_transaction(transaction)
            
            # Route to appropriate topic based on decision
            if decision.final_score > config.FRAUD_THRESHOLD_HIGH:
                topic = config.KAFKA_TOPIC_FRAUD_ALERTS
                self.fraud_count += 1
            else:
                topic = config.KAFKA_TOPIC_LEGITIMATE
                self.approved_count += 1
            
            if decision.decision == 'REVIEW':
                self.review_count += 1
            
            # Publish decision
            self.publish_decision(topic, decision)
            
            self.processed_count += 1
            
        except Exception as e:
            print(f"{Fore.RED}✗ Error processing transaction: {e}{Style.RESET_ALL}")
    
    def publish_decision(self, topic: str, decision: FraudDecision):
        """
        Publish fraud decision to Kafka
        
        Args:
            topic: Kafka topic to publish to
            decision: FraudDecision object
        """
        try:
            future = self.producer.send(
                topic,
                key=decision.transaction_id,
                value=decision.to_dict()
            )
            
            # Wait for send to complete
            future.get(timeout=10)
            
            topic_color = Fore.RED if topic == config.KAFKA_TOPIC_FRAUD_ALERTS else Fore.GREEN
            print(f"{topic_color}📤 Published to {topic}: {decision.transaction_id} | "
                  f"Decision: {decision.decision}{Style.RESET_ALL}\n")
            
        except KafkaError as e:
            print(f"{Fore.RED}✗ Error publishing decision: {e}{Style.RESET_ALL}")
    
    def print_statistics(self):
        """Print processing statistics"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 STATISTICS")
        print(f"{Fore.CYAN}{'='*80}")
        print(f"Total Processed: {self.processed_count}")
        print(f"{Fore.RED}Fraud Alerts: {self.fraud_count}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Review Required: {self.review_count}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Approved: {self.approved_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def run(self):
        """Run the consumer"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🤖 FRAUD DETECTION CONSUMER STARTED")
        print(f"{Fore.CYAN}Consuming from: {config.KAFKA_TOPIC_TRANSACTIONS}")
        print(f"{Fore.CYAN}Multi-Agent AI System: ACTIVE")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        try:
            for message in self.consumer:
                self.process_transaction(message.value)
                
                # Print statistics every 10 transactions
                if self.processed_count % 10 == 0:
                    self.print_statistics()
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Consumer stopped by user{Style.RESET_ALL}")
        finally:
            self.consumer.close()
            self.producer.close()
            self.print_statistics()


if __name__ == '__main__':
    consumer = FraudDetectionConsumer()
    consumer.run()
