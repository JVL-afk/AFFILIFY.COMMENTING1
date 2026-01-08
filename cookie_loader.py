# cookie_loader.py - LOADS ALL 29 ACCOUNTS FROM CSV

"""
AFFILIFY COOKIE LOADER
Processes tiktok_cookies.csv and creates properly formatted cookie files
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import logging
from logger_system import log_start, log_end, affilify_logger

logger = logging.getLogger(__name__)


class CookieVaultLoader:
    """
    Loads cookies from CSV vault and creates individual account files
    """
    
    def __init__(self, csv_path: str = "tiktok_cookies.csv", output_dir: str = "affilify_data/cookies"):
        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔓 Cookie Vault Loader initialized")
    
    def load_from_csv(self) -> dict:
        """
        Load all cookies from CSV and create individual account files
        
        Returns:
            Dict with processing summary
        """
        start = log_start("LoadCookiesFromCSV", csv_path=self.csv_path)
        
        affilify_logger.main_logger.info("="*80)
        affilify_logger.main_logger.info("🔓 OPENING THE COOKIE VAULT")
        affilify_logger.main_logger.info("="*80)
        
        try:
            # Group cookies by account
            cookies_by_account = defaultdict(list)
            total_rows = 0
            
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    total_rows += 1
                    account = row['Account']
                    
                    # Parse expiration date
                    expiration_timestamp = None
                    if row['ExpirationDate']:
                        try:
                            expiration_timestamp = float(row['ExpirationDate'])
                        except ValueError:
                            pass
                    
                    # Create cookie object
                    cookie = {
                        'name': row['Name'],
                        'value': row['Value'],
                        'domain': row['Domain'],
                        'path': row['Path'],
                        'expires': expiration_timestamp,
                        'secure': row['Secure'].lower() == 'true' if row['Secure'] else True,
                        'httpOnly': row['HttpOnly'].lower() == 'true' if row['HttpOnly'] else False,
                        'sameSite': row['SameSite'] if row['SameSite'] else 'Lax'
                    }
                    
                    cookies_by_account[account].append(cookie)
            
            affilify_logger.main_logger.info(f"\n📊 CSV Processing:")
            affilify_logger.main_logger.info(f"   Total Rows: {total_rows}")
            affilify_logger.main_logger.info(f"   Accounts Found: {len(cookies_by_account)}")
            affilify_logger.main_logger.info(f"   Total Cookies: {sum(len(c) for c in cookies_by_account.values())}")
            
            # Create individual cookie files
            affilify_logger.main_logger.info(f"\n📁 Creating Cookie Files:")
            
            created_files = []
            for account, cookies in cookies_by_account.items():
                # Create properly formatted cookie data
                cookie_data = {
                    'username': account,
                    'cookies': cookies,
                    'saved_at': datetime.now().isoformat(),
                    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
                }
                
                # Save to file
                output_file = self.output_dir / f"{account}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, indent=2)
                
                created_files.append(str(output_file))
                affilify_logger.main_logger.info(f"   ✅ {account}: {len(cookies)} cookies → {output_file.name}")
            
            # Summary
            summary = {
                'total_rows': total_rows,
                'accounts_processed': len(cookies_by_account),
                'total_cookies': sum(len(c) for c in cookies_by_account.values()),
                'files_created': created_files,
                'accounts': list(cookies_by_account.keys())
            }
            
            log_end("LoadCookiesFromCSV", start, True, **summary)
            
            affilify_logger.main_logger.info("\n" + "="*80)
            affilify_logger.main_logger.info("✅ COOKIE VAULT LOADED SUCCESSFULLY")
            affilify_logger.main_logger.info("="*80)
            affilify_logger.main_logger.info(f"\n🎉 {len(cookies_by_account)} accounts ready to dominate TikTok!")
            affilify_logger.main_logger.info("="*80 + "\n")
            
            return summary
            
        except FileNotFoundError:
            affilify_logger.main_logger.error(f"❌ CSV file not found: {self.csv_path}")
            log_end("LoadCookiesFromCSV", start, False, error="file_not_found")
            raise
        
        except Exception as e:
            affilify_logger.main_logger.error(f"❌ Error loading cookies: {e}")
            log_end("LoadCookiesFromCSV", start, False, error=str(e))
            raise
    
    def verify_all_accounts(self) -> dict:
        """
        Verify all created cookie files
        
        Returns:
            Dict with verification results
        """
        start = log_start("VerifyAllCookies")
        
        affilify_logger.main_logger.info("\n🔍 VERIFYING ALL COOKIE FILES...")
        
        results = {
            'valid': [],
            'missing': [],
            'expired': [],
            'invalid': []
        }
        
        # Get all JSON files in cookie directory
        cookie_files = list(self.output_dir.glob("*.json"))
        
        for cookie_file in cookie_files:
            username = cookie_file.stem
            
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check expiration
                expires_at = datetime.fromisoformat(data['expires_at'])
                days_remaining = (expires_at - datetime.now()).days
                
                if days_remaining > 0:
                    results['valid'].append(username)
                    affilify_logger.main_logger.info(f"   ✅ {username}: Valid ({days_remaining} days remaining)")
                else:
                    results['expired'].append(username)
                    affilify_logger.main_logger.warning(f"   ⚠️ {username}: EXPIRED")
                
            except Exception as e:
                results['invalid'].append(username)
                affilify_logger.main_logger.error(f"   ❌ {username}: Invalid ({e})")
        
        affilify_logger.main_logger.info(f"\n📊 Verification Summary:")
        affilify_logger.main_logger.info(f"   ✅ Valid: {len(results['valid'])}")
        affilify_logger.main_logger.info(f"   ⚠️ Expired: {len(results['expired'])}")
        affilify_logger.main_logger.info(f"   ❌ Invalid: {len(results['invalid'])}")
        
        log_end("VerifyAllCookies", start, True, **{k: len(v) for k, v in results.items()})
        
        return results
    
    def display_sample_cookie_file(self, username: str = None):
        """
        Display a sample cookie file for verification
        
        Args:
            username: Specific account to display (or first account if None)
        """
        if username is None:
            # Get first account
            cookie_files = list(self.output_dir.glob("*.json"))
            if not cookie_files:
                print("❌ No cookie files found")
                return
            username = cookie_files[0].stem
        
        cookie_file = self.output_dir / f"{username}.json"
        
        if not cookie_file.exists():
            print(f"❌ Cookie file not found for {username}")
            return
        
        with open(cookie_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("\n" + "="*80)
        print(f"📄 SAMPLE COOKIE FILE: {username}.json")
        print("="*80)
        print(json.dumps(data, indent=2))
        print("="*80 + "\n")


# Standalone execution
def main():
    """
    Main execution: Load cookies from CSV and verify
    """
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║              🔓 AFFILIFY COOKIE VAULT LOADER 🔓                    ║
║                                                                    ║
║                Processing TikTok Account Cookies                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize loader
    loader = CookieVaultLoader()
    
    # Load from CSV
    summary = loader.load_from_csv()
    
    # Verify all accounts
    verification = loader.verify_all_accounts()
    
    # Display sample
    if summary['accounts']:
        loader.display_sample_cookie_file(summary['accounts'][0])
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 COOKIE VAULT PROCESSING COMPLETE")
    print("="*80)
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   Total Accounts: {summary['accounts_processed']}")
    print(f"   Total Cookies: {summary['total_cookies']}")
    print(f"   Valid Accounts: {len(verification['valid'])}")
    print(f"   Ready to Use: {len(verification['valid'])} accounts")
    print("\n🚀 READY TO DOMINATE TIKTOK!")
    print("="*80 + "\n")
    
    print("Next steps:")
    print("1. Run: python main_launcher.py")
    print("2. Start automated campaign")
    print("3. Watch the leads roll in! 💰\n")


if __name__ == "__main__":
    main()
