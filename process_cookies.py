# process_cookies.py - COOKIE VAULT PROCESSOR

"""
Processes the tiktok_cookies.csv and creates properly formatted
cookie files for all 29 accounts
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

def process_tiktok_cookies_csv(csv_path: str = "tiktok_cookies.csv"):
    """
    Process the CSV and create individual cookie files for each account
    """
    print("🔓 OPENING THE VAULT...")
    print("="*70)
    
    # Read CSV
    cookies_by_account = defaultdict(list)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            account = row['Account']
            
            # Convert ExpirationDate to proper format
            expiration_timestamp = float(row['ExpirationDate']) if row['ExpirationDate'] else None
            
            cookie = {
                'name': row['Name'],
                'value': row['Value'],
                'domain': row['Domain'],
                'path': row['Path'],
                'expires': expiration_timestamp,
                'secure': row['Secure'].lower() == 'true',
                'httpOnly': row['HttpOnly'].lower() == 'true',
                'sameSite': row['SameSite'] if row['SameSite'] else 'Lax'
            }
            
            cookies_by_account[account].append(cookie)
    
    print(f"✅ Found {len(cookies_by_account)} accounts")
    print(f"✅ Total cookies: {sum(len(cookies) for cookies in cookies_by_account.values())}")
    print()
    
    # Create cookie files
    output_dir = Path("affilify_data/cookies")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for account, cookies in cookies_by_account.items():
        # Format account data
        cookie_data = {
            'username': account,
            'cookies': cookies,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        # Save to file
        output_file = output_dir / f"{account}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cookie_data, f, indent=2)
        
        print(f"✅ Created: {output_file} ({len(cookies)} cookies)")
    
    print()
    print("="*70)
    print("🎉 ALL COOKIE FILES CREATED SUCCESSFULLY!")
    print("="*70)
    
    # Return the complete data for one account as example
    first_account = list(cookies_by_account.keys())[0]
    return {
        'accounts_processed': len(cookies_by_account),
        'total_cookies': sum(len(cookies) for cookies in cookies_by_account.values()),
        'sample_account': first_account,
        'sample_data': {
            'username': first_account,
            'cookies': cookies_by_account[first_account],
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
    }


# Execute
if __name__ == "__main__":
    result = process_tiktok_cookies_csv()
    
    print("\n" + "="*70)
    print("📊 PROCESSING SUMMARY")
    print("="*70)
    print(f"Accounts Processed: {result['accounts_processed']}")
    print(f"Total Cookies: {result['total_cookies']}")
    print(f"Sample Account: {result['sample_account']}")
    print()
    print("🔥 READY TO DOMINATE TIKTOK!")
    print("="*70)
