"""
Kafka Admin - Topic management and health checks
"""
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError
from colorama import Fore, Style, init
import config

# Initialize colorama
init(autoreset=True)


class KafkaAdmin:
    """Kafka administration utilities"""
    
    def __init__(self):
        """Initialize Kafka admin client"""
        try:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                client_id='fraud-detection-admin'
            )
            print(f"{Fore.GREEN}✓ Connected to Kafka{Style.RESET_ALL}")
        except KafkaError as e:
            print(f"{Fore.RED}✗ Failed to connect to Kafka: {e}{Style.RESET_ALL}")
            raise
    
    def create_topics(self):
        """Create required Kafka topics"""
        topics = [
            NewTopic(
                name=config.KAFKA_TOPIC_TRANSACTIONS,
                num_partitions=3,
                replication_factor=1
            ),
            NewTopic(
                name=config.KAFKA_TOPIC_FRAUD_ALERTS,
                num_partitions=3,
                replication_factor=1
            ),
            NewTopic(
                name=config.KAFKA_TOPIC_LEGITIMATE,
                num_partitions=3,
                replication_factor=1
            )
        ]
        
        print(f"\n{Fore.CYAN}Creating Kafka topics...{Style.RESET_ALL}")
        
        for topic in topics:
            try:
                self.admin_client.create_topics([topic], validate_only=False)
                print(f"{Fore.GREEN}✓ Created topic: {topic.name}{Style.RESET_ALL}")
            except TopicAlreadyExistsError:
                print(f"{Fore.YELLOW}⚠ Topic already exists: {topic.name}{Style.RESET_ALL}")
            except KafkaError as e:
                print(f"{Fore.RED}✗ Error creating topic {topic.name}: {e}{Style.RESET_ALL}")
    
    def list_topics(self):
        """List all Kafka topics"""
        try:
            topics = self.admin_client.list_topics()
            print(f"\n{Fore.CYAN}Available topics:{Style.RESET_ALL}")
            for topic in topics:
                if not topic.startswith('__'):  # Skip internal topics
                    print(f"  • {topic}")
        except KafkaError as e:
            print(f"{Fore.RED}✗ Error listing topics: {e}{Style.RESET_ALL}")
    
    def verify_setup(self):
        """Verify Kafka setup"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🔍 VERIFYING KAFKA SETUP")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        required_topics = [
            config.KAFKA_TOPIC_TRANSACTIONS,
            config.KAFKA_TOPIC_FRAUD_ALERTS,
            config.KAFKA_TOPIC_LEGITIMATE
        ]
        
        try:
            existing_topics = self.admin_client.list_topics()
            
            all_exist = True
            for topic in required_topics:
                if topic in existing_topics:
                    print(f"{Fore.GREEN}✓ Topic exists: {topic}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}✗ Topic missing: {topic}{Style.RESET_ALL}")
                    all_exist = False
            
            if all_exist:
                print(f"\n{Fore.GREEN}✓ All required topics are ready!{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠ Some topics are missing. Run create_topics(){Style.RESET_ALL}")
                
        except KafkaError as e:
            print(f"{Fore.RED}✗ Error verifying setup: {e}{Style.RESET_ALL}")
    
    def close(self):
        """Close admin client"""
        self.admin_client.close()


def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Admin Utilities')
    parser.add_argument('--create', action='store_true', help='Create topics')
    parser.add_argument('--list', action='store_true', help='List topics')
    parser.add_argument('--verify', action='store_true', help='Verify setup')
    
    args = parser.parse_args()
    
    admin = KafkaAdmin()
    
    try:
        if args.create:
            admin.create_topics()
        
        if args.list:
            admin.list_topics()
        
        if args.verify:
            admin.verify_setup()
        
        # Default: create and verify
        if not (args.create or args.list or args.verify):
            admin.create_topics()
            admin.verify_setup()
            
    finally:
        admin.close()


if __name__ == '__main__':
    main()
