"""
Kafka Streams Implementation using Faust
Implements KTable and Velocity Windows for rapid-fire attack detection
Matches the architecture diagram with:
- KStream: transactions topic
- KTable: Velocity Context (stateful store)
- 5-min tumbling windows for velocity calculation
- Stream enrichment with leftJoins
"""
import faust
from faust import windows
from datetime import datetime, timedelta
from typing import Optional
import config
import json

# ============================================================================
# FAUST APP CONFIGURATION
# ============================================================================

app = faust.App(
    'fraud-detection-streams',
    broker=f'kafka://{config.KAFKA_BOOTSTRAP_SERVERS}',
    store='rocksdb://',  # Persistent state store (KTable backing)
    value_serializer='json',
    origin='kafka_streams',
    autodiscover=True,
    topic_replication_factor=1,
)

# ============================================================================
# DATA MODELS (Faust Records = Kafka Message Schemas)
# ============================================================================

class Transaction(faust.Record, serializer='json'):
    """Transaction record from 'transactions' topic (KStream)"""
    transaction_id: str
    timestamp: str
    customer_id: str
    amount: float
    currency: str
    merchant_name: str
    merchant_category: str
    location: str
    payment_method: str


class CustomerProfile(faust.Record, serializer='json'):
    """Customer profile from 'customerProfiles' topic (KTable source)"""
    customer_id: str
    average_transaction_amount: float
    daily_spending_limit: float
    transaction_categories: list
    primary_location: str
    risk_level: str


class VelocityContext(faust.Record, serializer='json'):
    """Velocity context computed from 5-min tumbling window (KTable)"""
    customer_id: str
    transaction_count: int
    total_amount: float
    avg_amount: float
    unique_locations: list
    unique_merchants: list
    time_span_minutes: float
    velocity_score: float  # transactions per minute
    rapid_fire_detected: bool
    window_start: str
    window_end: str


class EnrichedTransaction(faust.Record, serializer='json'):
    """Enriched transaction after joins (KStream output)"""
    # Original transaction fields
    transaction_id: str
    timestamp: str
    customer_id: str
    amount: float
    currency: str
    merchant_name: str
    merchant_category: str
    location: str
    payment_method: str
    # Enrichment from customerProfiles (leftJoin)
    customer_avg_amount: Optional[float] = None
    customer_daily_limit: Optional[float] = None
    customer_primary_location: Optional[str] = None
    customer_risk_level: Optional[str] = None
    customer_typical_categories: Optional[list] = None
    # Enrichment from velocity context (leftJoin)
    velocity_transaction_count: int = 0
    velocity_total_amount: float = 0.0
    velocity_score: float = 0.0
    rapid_fire_detected: bool = False
    location_hopping: bool = False
    merchant_hopping: bool = False


# ============================================================================
# KAFKA TOPICS
# ============================================================================

# Input topics
transactions_topic = app.topic('transactions', value_type=Transaction)
customer_profiles_topic = app.topic('customerProfiles', value_type=CustomerProfile)

# Output topics
enriched_transactions_topic = app.topic('enriched-transactions', value_type=EnrichedTransaction)
velocity_context_topic = app.topic('velocity-context', value_type=VelocityContext)

# ============================================================================
# KTABLE: Customer Profiles (GlobalTable for broadcast join)
# ============================================================================

# This is the KTable for customer profiles - backed by RocksDB state store
# GlobalTable = replicated to all partitions for fast local lookups
customer_profiles_table = app.GlobalTable(
    'customer-profiles-table',
    default=None,
    key_type=str,
    value_type=CustomerProfile,
)


# ============================================================================
# KTABLE: Velocity Context (Windowed aggregation with tumbling window)
# ============================================================================

# 5-minute tumbling window for velocity calculation
VELOCITY_WINDOW = windows.TumblingWindow(size=timedelta(minutes=5))

# Velocity aggregation table - stores windowed counts
velocity_table = app.Table(
    'velocity-context-table',
    default=lambda: {
        'transaction_count': 0,
        'total_amount': 0.0,
        'locations': [],
        'merchants': [],
        'first_timestamp': None,
        'last_timestamp': None,
    },
    key_type=str,
    partitions=1,
).tumbling(VELOCITY_WINDOW, expires=timedelta(minutes=15))


# ============================================================================
# STREAM PROCESSOR: Customer Profiles → KTable
# ============================================================================

@app.agent(customer_profiles_topic)
async def process_customer_profiles(profiles):
    """
    Consume customerProfiles topic and populate KTable
    This provides the static customer profile for enrichment
    """
    async for profile in profiles:
        # Update the GlobalTable with customer profile
        customer_profiles_table[profile.customer_id] = profile
        print(f"📋 KTable Updated: Customer profile for {profile.customer_id}")


# ============================================================================
# STREAM PROCESSOR: Transactions → Velocity Window → KTable
# ============================================================================

@app.agent(transactions_topic)
async def calculate_velocity(transactions):
    """
    Process transactions stream through 5-min tumbling window
    Updates velocity KTable and detects rapid-fire attacks
    
    Architecture: transactions (KStream) → 5-min window → Velocity Context (KTable)
    """
    async for tx in transactions:
        customer_id = tx.customer_id
        
        # Get current window state from velocity table
        current = velocity_table[customer_id].value()
        
        # Update velocity metrics
        current['transaction_count'] += 1
        current['total_amount'] += tx.amount
        
        # Track unique locations (for location hopping detection)
        if tx.location not in current['locations']:
            current['locations'].append(tx.location)
        
        # Track unique merchants (for merchant hopping detection)
        if tx.merchant_name not in current['merchants']:
            current['merchants'].append(tx.merchant_name)
        
        # Update timestamps
        if current['first_timestamp'] is None:
            current['first_timestamp'] = tx.timestamp
        current['last_timestamp'] = tx.timestamp
        
        # Calculate time span
        try:
            first_ts = datetime.fromisoformat(current['first_timestamp'])
            last_ts = datetime.fromisoformat(current['last_timestamp'])
            time_span = (last_ts - first_ts).total_seconds() / 60
        except:
            time_span = 0.0
        
        # Calculate velocity score (transactions per minute)
        velocity_score = current['transaction_count'] / max(time_span, 1)
        
        # Detect rapid-fire attack
        rapid_fire = (
            current['transaction_count'] > 15 or  # More than 15 txns in 5 min
            velocity_score > 3.0  # More than 3 txns per minute
        )
        
        # Update velocity table (KTable)
        velocity_table[customer_id] = current
        
        # Create velocity context record
        velocity_context = VelocityContext(
            customer_id=customer_id,
            transaction_count=current['transaction_count'],
            total_amount=current['total_amount'],
            avg_amount=current['total_amount'] / current['transaction_count'],
            unique_locations=current['locations'],
            unique_merchants=current['merchants'],
            time_span_minutes=time_span,
            velocity_score=velocity_score,
            rapid_fire_detected=rapid_fire,
            window_start=current['first_timestamp'] or tx.timestamp,
            window_end=current['last_timestamp'] or tx.timestamp,
        )
        
        # Publish velocity context to topic (for downstream consumers)
        await velocity_context_topic.send(key=customer_id, value=velocity_context)
        
        # Log rapid-fire detection
        if rapid_fire:
            print(f"🚨 RAPID-FIRE DETECTED: Customer {customer_id}")
            print(f"   └─ {current['transaction_count']} txns in {time_span:.1f} min")
            print(f"   └─ Velocity: {velocity_score:.2f} txn/min")
        
        # Perform stream enrichment with leftJoins
        await enrich_and_emit(tx, velocity_context)


# ============================================================================
# STREAMING ENRICHMENT LAYER (leftJoins)
# ============================================================================

async def enrich_and_emit(tx: Transaction, velocity: VelocityContext):
    """
    Perform streaming enrichment with leftJoins:
    1. Transaction + Velocity Context (leftJoin)
    2. Transaction + Customer Profile (leftJoin)
    
    Output: EnrichedTransaction (KStream)
    """
    customer_id = tx.customer_id
    
    # LeftJoin with Customer Profile (from KTable)
    profile = customer_profiles_table.get(customer_id)
    
    # Build enriched transaction
    enriched = EnrichedTransaction(
        # Original transaction
        transaction_id=tx.transaction_id,
        timestamp=tx.timestamp,
        customer_id=tx.customer_id,
        amount=tx.amount,
        currency=tx.currency,
        merchant_name=tx.merchant_name,
        merchant_category=tx.merchant_category,
        location=tx.location,
        payment_method=tx.payment_method,
        # Customer profile enrichment (leftJoin - may be None)
        customer_avg_amount=profile.average_transaction_amount if profile else None,
        customer_daily_limit=profile.daily_spending_limit if profile else None,
        customer_primary_location=profile.primary_location if profile else None,
        customer_risk_level=profile.risk_level if profile else None,
        customer_typical_categories=profile.transaction_categories if profile else None,
        # Velocity context enrichment
        velocity_transaction_count=velocity.transaction_count,
        velocity_total_amount=velocity.total_amount,
        velocity_score=velocity.velocity_score,
        rapid_fire_detected=velocity.rapid_fire_detected,
        location_hopping=len(velocity.unique_locations) > 3,
        merchant_hopping=len(velocity.unique_merchants) > 5,
    )
    
    # Emit to enriched-transactions topic
    await enriched_transactions_topic.send(key=tx.transaction_id, value=enriched)
    
    print(f"✅ Enriched: {tx.transaction_id}")
    print(f"   └─ Velocity: {velocity.transaction_count} txns @ {velocity.velocity_score:.2f}/min")
    print(f"   └─ Rapid-fire: {velocity.rapid_fire_detected}")


# ============================================================================
# HELPER: Get current velocity context for a customer
# ============================================================================

def get_velocity_context(customer_id: str) -> dict:
    """
    Get current velocity context from KTable
    This is used by the production coordinator for AI analysis
    """
    try:
        current = velocity_table[customer_id].value()
        if current and current['transaction_count'] > 0:
            time_span = 0.0
            if current['first_timestamp'] and current['last_timestamp']:
                try:
                    first_ts = datetime.fromisoformat(current['first_timestamp'])
                    last_ts = datetime.fromisoformat(current['last_timestamp'])
                    time_span = (last_ts - first_ts).total_seconds() / 60
                except:
                    pass
            
            velocity_score = current['transaction_count'] / max(time_span, 1)
            
            return {
                'transaction_count': current['transaction_count'],
                'total_amount': current['total_amount'],
                'avg_amount': current['total_amount'] / current['transaction_count'],
                'unique_locations': len(current['locations']),
                'unique_merchants': len(current['merchants']),
                'time_span_minutes': time_span,
                'velocity_score': velocity_score,
                'rapid_fire_detected': current['transaction_count'] > 15 or velocity_score > 3.0,
            }
    except:
        pass
    
    return {
        'transaction_count': 0,
        'total_amount': 0.0,
        'avg_amount': 0.0,
        'unique_locations': 0,
        'unique_merchants': 0,
        'time_span_minutes': 0,
        'velocity_score': 0,
        'rapid_fire_detected': False,
    }


def get_customer_profile(customer_id: str) -> Optional[dict]:
    """
    Get customer profile from KTable
    """
    profile = customer_profiles_table.get(customer_id)
    if profile:
        return {
            'customer_id': profile.customer_id,
            'average_transaction_amount': profile.average_transaction_amount,
            'daily_spending_limit': profile.daily_spending_limit,
            'transaction_categories': profile.transaction_categories,
            'primary_location': profile.primary_location,
            'risk_level': profile.risk_level,
        }
    return None


# ============================================================================
# APP STARTUP / LIFECYCLE
# ============================================================================

@app.on_started.connect
async def on_started(app, **kwargs):
    """Called when Faust app starts"""
    print("=" * 60)
    print("🚀 Kafka Streams (Faust) Started!")
    print("=" * 60)
    print("📊 Architecture Components:")
    print("   ├─ KStream: transactions topic")
    print("   ├─ KTable: customer-profiles-table")
    print("   ├─ KTable: velocity-context-table (5-min window)")
    print("   └─ KStream: enriched-transactions topic")
    print("=" * 60)


# ============================================================================
# RUN WORKER
# ============================================================================

if __name__ == '__main__':
    app.main()
