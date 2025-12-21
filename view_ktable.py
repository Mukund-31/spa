"""
View KTable Contents
Shows all data stored in the RocksDB KTables
"""
from rocksdict import Rdict, AccessType
import json
import os

def view_ktables():
    print("=" * 70)
    print("📊 KTABLE VIEWER")
    print("=" * 70)
    
    state_dir = './ktable_state'
    
    # ==========================================
    # View Velocity KTable
    # ==========================================
    velocity_path = os.path.join(state_dir, 'velocity_ktable')
    
    if os.path.exists(velocity_path):
        print("\n📈 VELOCITY KTABLE (velocity_ktable)")
        print("-" * 70)
        
        db = Rdict(velocity_path, access_type=AccessType.secondary(f'{velocity_path}_secondary'))
        count = 0
        
        for key in db.keys():
            value = db.get(key)
            if value:
                data = json.loads(value)
                count += 1
                
                # Parse transactions
                txns = data.get('transactions', [])
                
                print(f"\n🔑 Key: {key}")
                print(f"   📊 Transactions in window: {len(txns)}")
                
                if txns:
                    # Calculate velocity
                    total_amount = sum(t['amount'] for t in txns)
                    merchants = set(t['merchant'] for t in txns)
                    
                    print(f"   💰 Total amount: ₹{total_amount:,.2f}")
                    print(f"   🏪 Unique merchants: {len(merchants)}")
                    print(f"   ⏰ Window: {data.get('window_start', 'N/A')} → {data.get('window_end', 'N/A')}")
                    
                    # Show latest 3 transactions
                    print(f"\n   📜 Latest transactions:")
                    for t in txns[-3:]:
                        print(f"      • ₹{t['amount']:,.2f} at {t['merchant']} ({t['timestamp'][:19]})")
        
        db.close()
        
        if count == 0:
            print("   (empty - no velocity data yet)")
        else:
            print(f"\n   ✅ Total customers in table: {count}")
    else:
        print("\n❌ Velocity KTable not found at:", velocity_path)
    
    # ==========================================
    # View Customer Profile KTable
    # ==========================================
    profile_path = os.path.join(state_dir, 'customer_profiles_ktable')
    
    if os.path.exists(profile_path):
        print("\n\n👤 CUSTOMER PROFILE KTABLE (customer_profiles_ktable)")
        print("-" * 70)
        
        db = Rdict(profile_path, access_type=AccessType.secondary(f'{profile_path}_secondary'))
        count = 0
        
        for key in db.keys():
            value = db.get(key)
            if value:
                data = json.loads(value)
                count += 1
                
                print(f"\n🔑 Key: {key}")
                print(f"   👤 Customer ID: {data.get('customer_id', 'N/A')}")
                print(f"   💰 Avg Transaction: ₹{data.get('average_transaction_amount', 0):,.2f}")
                print(f"   📍 Primary Location: {data.get('primary_location', 'N/A')}")
                print(f"   ⚠️  Risk Level: {data.get('risk_level', 'N/A')}")
                print(f"   💳 Daily Limit: ₹{data.get('daily_spending_limit', 0):,.2f}")
                print(f"   🏷️  Categories: {data.get('transaction_categories', [])}")
        
        db.close()
        
        if count == 0:
            print("   (empty - no customer profiles yet)")
        else:
            print(f"\n   ✅ Total profiles in table: {count}")
    else:
        print("\n❌ Customer Profile KTable not found at:", profile_path)
    
    print("\n" + "=" * 70)
    print("📂 KTable files location:", os.path.abspath(state_dir))
    print("=" * 70)


if __name__ == '__main__':
    view_ktables()
