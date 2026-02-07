#!/usr/bin/env python3.11
"""
Convert TikTok cookies from CSV format to JSON format for the automation system
"""
import csv
import json
import os

def convert_csv_to_json():
    """Convert tiktok_cookies.csv to individual JSON files"""
    
    csv_path = "/home/ubuntu/upload/tiktok_cookies.csv"
    output_dir = "/home/ubuntu/AFFILIFY.COMMENTING1/affilify_data/cookies"
    
    print("="*80)
    print("🍪 CONVERTING FRESH COOKIES FROM CSV TO JSON")
    print("="*80)
    
    # Create backup of old cookies
    backup_dir = f"{output_dir}_backup"
    if os.path.exists(output_dir):
        print(f"📦 Backing up old cookies to: {backup_dir}")
        os.system(f"cp -r {output_dir} {backup_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read CSV and convert
    converted_count = 0
    with open(csv_path, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:  # Skip header
                continue
            if not line.strip():
                continue
            parts = line.strip().split(',', 1)  # Split on first comma only
            if len(parts) != 2:
                continue
            account_name = parts[0]
            # Remove surrounding quotes and unescape double quotes
            json_str = parts[1].strip()
            if json_str.startswith('"') and json_str.endswith('"'):
                json_str = json_str[1:-1]  # Remove outer quotes
            json_str = json_str.replace('""', '"')  # Unescape double quotes
            cookie_data = json.loads(json_str)
            
            # Save to JSON file
            output_path = f"{output_dir}/{account_name}.json"
            with open(output_path, 'w') as out_f:
                json.dump(cookie_data, out_f, indent=2)
            
            num_cookies = len(cookie_data['cookies'])
            print(f"✅ {account_name}: {num_cookies} cookies saved to {output_path}")
            converted_count += 1
    
    print("="*80)
    print(f"🎉 CONVERSION COMPLETE!")
    print(f"   Converted: {converted_count} accounts")
    print(f"   Location: {output_dir}")
    print("="*80)
    
    return converted_count

if __name__ == "__main__":
    convert_csv_to_json()
