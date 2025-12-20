"""
Main orchestration script - Runs the complete fraud detection system
"""
import threading
import time
import signal
import sys
from colorama import Fore, Style, init
from kafka_admin import KafkaAdmin
from producer import TransactionProducer
from consumer import FraudDetectionConsumer

# Initialize colorama
init(autoreset=True)

# Global flag for graceful shutdown
shutdown_flag = threading.Event()


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n{Fore.YELLOW}Shutting down gracefully...{Style.RESET_ALL}")
    shutdown_flag.set()


def run_producer():
    """Run transaction producer"""
    try:
        producer = TransactionProducer()
        
        while not shutdown_flag.is_set():
            # Generate and publish one transaction
            suspicious = __import__('random').random() < 0.1
            transaction = producer.generate_transaction(suspicious)
            producer.publish_transaction(transaction)
            
            # Wait based on configured rate
            time.sleep(1.0 / __import__('config').TRANSACTION_RATE)
            
    except Exception as e:
        print(f"{Fore.RED}Producer error: {e}{Style.RESET_ALL}")


def run_consumer():
    """Run fraud detection consumer"""
    try:
        consumer = FraudDetectionConsumer()
        consumer.run()
    except Exception as e:
        print(f"{Fore.RED}Consumer error: {e}{Style.RESET_ALL}")


def main():
    """Main orchestration function"""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"\n{Fore.CYAN}{'='*80}")
    print(f"{Fore.CYAN}🚀 KAFKA FRAUD DETECTION SYSTEM")
    print(f"{Fore.CYAN}Multi-Agent AI Powered by Gemini")
    print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    # Step 1: Setup Kafka topics
    print(f"{Fore.CYAN}Step 1: Setting up Kafka topics...{Style.RESET_ALL}")
    try:
        admin = KafkaAdmin()
        admin.create_topics()
        admin.verify_setup()
        admin.close()
        print(f"{Fore.GREEN}✓ Kafka setup complete{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}✗ Kafka setup failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Make sure Docker containers are running: docker-compose up -d{Style.RESET_ALL}")
        return
    
    # Step 2: Start consumer in a separate thread
    print(f"{Fore.CYAN}Step 2: Starting fraud detection consumer...{Style.RESET_ALL}")
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    time.sleep(2)  # Give consumer time to start
    
    # Step 3: Start producer in a separate thread
    print(f"{Fore.CYAN}Step 3: Starting transaction producer...{Style.RESET_ALL}")
    producer_thread = threading.Thread(target=run_producer, daemon=True)
    producer_thread.start()
    
    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}✓ SYSTEM RUNNING")
    print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}📊 View Kafka UI at: http://localhost:8080{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop{Style.RESET_ALL}\n")
    
    # Wait for shutdown signal
    try:
        while not shutdown_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    
    print(f"\n{Fore.CYAN}Waiting for threads to finish...{Style.RESET_ALL}")
    consumer_thread.join(timeout=5)
    producer_thread.join(timeout=5)
    
    print(f"{Fore.GREEN}✓ System stopped{Style.RESET_ALL}\n")


if __name__ == '__main__':
    main()
