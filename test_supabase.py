
from modules.data.supabase_client import SupabaseManager
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def test_supabase():
    print("Testing Supabase Connection...")
    client = SupabaseManager()
    
    if client.is_connected:
        print("✅ Connection Successful")
        
        print("Fetching accounts...")
        accounts = client.fetch_accounts()
        
        if accounts:
            print(f"✅ Fetched {len(accounts)} accounts")
            print("Sample account:", accounts[0])
            
            # Verify PIN is present
            if accounts[0].get('pin'):
                print(f"✅ PIN found for first account: {accounts[0]['pin']}")
            else:
                print("❌ PIN MISSING in first account!")
        else:
            print("⚠️ No accounts found or fetch failed (check logs)")
            
    else:
        print("❌ Connection Failed")

if __name__ == "__main__":
    test_supabase()
