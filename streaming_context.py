"""
Streaming Context Store - Tracks customer velocity, profiles, and patterns
"""
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading


class StreamingContextStore:
    """
    In-memory store for streaming context intelligence
    Tracks customer behavior patterns for velocity-based fraud detection
    """
    
    def __init__(self, velocity_window_minutes: int = 10):
        """
        Initialize streaming context store
        
        Args:
            velocity_window_minutes: Time window for velocity tracking
        """
        self.velocity_window = timedelta(minutes=velocity_window_minutes)
        
        # Customer transaction history (last N minutes)
        self.customer_transactions = defaultdict(deque)
        
        # Customer profiles (aggregated stats)
        self.customer_profiles = defaultdict(lambda: {
            'total_transactions': 0,
            'total_amount': 0.0,
            'avg_amount': 0.0,
            'locations': set(),
            'merchants': set(),
            'payment_methods': set(),
            'first_seen': None,
            'last_seen': None
        })
        
        # Location patterns
        self.location_patterns = defaultdict(int)
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
    
    def add_transaction(self, transaction: dict):
        """
        Add transaction to streaming context
        
        Args:
            transaction: Transaction dictionary
        """
        with self.lock:
            customer_id = transaction['customer_id']
            timestamp = datetime.fromisoformat(transaction['timestamp'])
            
            # Add to velocity tracking
            self.customer_transactions[customer_id].append({
                'timestamp': timestamp,
                'amount': transaction['amount'],
                'location': transaction['location'],
                'merchant': transaction['merchant_name'],
                'payment_method': transaction['payment_method']
            })
            
            # Clean old transactions outside velocity window
            self._clean_old_transactions(customer_id, timestamp)
            
            # Update customer profile
            profile = self.customer_profiles[customer_id]
            profile['total_transactions'] += 1
            profile['total_amount'] += transaction['amount']
            profile['avg_amount'] = profile['total_amount'] / profile['total_transactions']
            profile['locations'].add(transaction['location'])
            profile['merchants'].add(transaction['merchant_name'])
            profile['payment_methods'].add(transaction['payment_method'])
            
            if profile['first_seen'] is None:
                profile['first_seen'] = timestamp
            profile['last_seen'] = timestamp
            
            # Update location patterns
            self.location_patterns[transaction['location']] += 1
    
    def get_velocity_context(self, customer_id: str) -> Dict:
        """
        Get velocity context for a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dictionary with velocity metrics
        """
        with self.lock:
            transactions = list(self.customer_transactions[customer_id])
            
            if not transactions:
                return {
                    'transaction_count': 0,
                    'total_amount': 0.0,
                    'avg_amount': 0.0,
                    'unique_locations': 0,
                    'unique_merchants': 0,
                    'time_span_minutes': 0,
                    'velocity_score': 0
                }
            
            total_amount = sum(t['amount'] for t in transactions)
            unique_locations = len(set(t['location'] for t in transactions))
            unique_merchants = len(set(t['merchant'] for t in transactions))
            
            # Calculate time span
            timestamps = [t['timestamp'] for t in transactions]
            time_span = (max(timestamps) - min(timestamps)).total_seconds() / 60
            
            # Velocity score (transactions per minute)
            velocity_score = len(transactions) / max(time_span, 1)
            
            return {
                'transaction_count': len(transactions),
                'total_amount': total_amount,
                'avg_amount': total_amount / len(transactions),
                'unique_locations': unique_locations,
                'unique_merchants': unique_merchants,
                'time_span_minutes': time_span,
                'velocity_score': velocity_score
            }
    
    def get_customer_profile(self, customer_id: str) -> Dict:
        """
        Get customer profile
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer profile dictionary
        """
        with self.lock:
            profile = self.customer_profiles[customer_id].copy()
            # Convert sets to lists for JSON serialization
            profile['locations'] = list(profile['locations'])
            profile['merchants'] = list(profile['merchants'])
            profile['payment_methods'] = list(profile['payment_methods'])
            return profile
    
    def get_streaming_context(self, customer_id: str, current_transaction: dict) -> Dict:
        """
        Get complete streaming context for fraud analysis
        
        Args:
            customer_id: Customer ID
            current_transaction: Current transaction being analyzed
            
        Returns:
            Complete streaming context
        """
        velocity = self.get_velocity_context(customer_id)
        profile = self.get_customer_profile(customer_id)
        
        # Calculate anomaly indicators
        amount_deviation = 0
        if profile['avg_amount'] > 0:
            amount_deviation = abs(current_transaction['amount'] - profile['avg_amount']) / profile['avg_amount']
        
        # Location anomaly
        location_is_new = current_transaction['location'] not in profile['locations']
        
        # Velocity alert
        velocity_alert = velocity['transaction_count'] > 10 or velocity['velocity_score'] > 1.0
        
        return {
            'velocity': velocity,
            'profile': profile,
            'anomalies': {
                'amount_deviation_pct': amount_deviation * 100,
                'location_is_new': location_is_new,
                'velocity_alert': velocity_alert,
                'rapid_fire_detected': velocity['transaction_count'] > 15
            },
            'risk_indicators': {
                'high_velocity': velocity['transaction_count'] > 10,
                'amount_spike': amount_deviation > 5.0,  # 500% deviation
                'location_hopping': velocity['unique_locations'] > 3,
                'merchant_hopping': velocity['unique_merchants'] > 5
            }
        }
    
    def _clean_old_transactions(self, customer_id: str, current_time: datetime):
        """Remove transactions outside velocity window"""
        cutoff_time = current_time - self.velocity_window
        transactions = self.customer_transactions[customer_id]
        
        while transactions and transactions[0]['timestamp'] < cutoff_time:
            transactions.popleft()
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        with self.lock:
            return {
                'total_customers': len(self.customer_profiles),
                'active_customers': len(self.customer_transactions),
                'total_locations': len(self.location_patterns),
                'most_common_locations': sorted(
                    self.location_patterns.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }
