# cookie_manager.py - SECURE SESSION HANDLER

"""
AFFILIFY COOKIE MANAGER
Handles secure cookie-based authentication for TikTok accounts
Allows VAs to work without knowing passwords
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import asyncio
from typing import Optional, Dict, List
from logger_system import log_start, log_end, log_error, log_account

logger = logging.getLogger(__name__)


class CookieManager:
    """
    Manages cookie-based authentication for TikTok accounts
    Allows VAs to work without knowing passwords
    """
    
    def __init__(self, cookies_dir: str = "affilify_data/cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.active_contexts = {}
        
        logger.info("🍪 Cookie Manager initialized")
    
    def save_cookies(self, username: str, cookies: List[Dict]) -> Path:
        """
        Save cookies to file after manual login
        
        Args:
            username: TikTok username
            cookies: List of cookie dictionaries from browser
            
        Returns:
            Path to saved cookie file
        """
        start = log_start("SaveCookies", username=username)
        
        cookie_file = self.cookies_dir / f"{username}.json"
        
        cookie_data = {
            'username': username,
            'cookies': cookies,
            'saved_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        try:
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            log_account(username, "SaveCookies", "SUCCESS", file=str(cookie_file))
            log_end("SaveCookies", start, True)
            
            logger.info(f"✅ Cookies saved for {username}")
            return cookie_file
            
        except Exception as e:
            log_error("SaveCookies", str(e), context={'username': username})
            log_end("SaveCookies", start, False, error=str(e))
            raise
    
    def load_cookies(self, username: str) -> Optional[Dict]:
        """
        Load cookies from file
        
        Args:
            username: TikTok username
            
        Returns:
            Cookie data dict or None if not found/expired
        """
        start = log_start("LoadCookies", username=username)
        
        cookie_file = self.cookies_dir / f"{username}.json"
        
        if not cookie_file.exists():
            log_error("LoadCookies", f"Cookie file not found for {username}")
            log_end("LoadCookies", start, False, reason="file_not_found")
            return None
        
        try:
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Check if cookies are expired
            expires_at = datetime.fromisoformat(cookie_data['expires_at'])
            if datetime.now() > expires_at:
                logger.warning(f"⚠️ Cookies expired for {username}. Please re-login manually.")
                log_account(username, "LoadCookies", "EXPIRED")
                log_end("LoadCookies", start, False, reason="expired")
                return None
            
            log_account(username, "LoadCookies", "SUCCESS", 
                       days_remaining=(expires_at - datetime.now()).days)
            log_end("LoadCookies", start, True)
            
            return cookie_data
            
        except Exception as e:
            log_error("LoadCookies", str(e), context={'username': username})
            log_end("LoadCookies", start, False, error=str(e))
            return None
    
    async def create_browser_context(self, username: str, headless: bool = True):
        """
        Create a Playwright browser context with loaded cookies
        
        Args:
            username: TikTok username
            headless: Run browser in headless mode (default True)
            
        Returns:
            Browser context object or None
        """
        start = log_start("CreateBrowserContext", username=username, headless=headless)
        
        cookie_data = self.load_cookies(username)
        if not cookie_data:
            log_end("CreateBrowserContext", start, False, reason="no_cookies")
            return None
        
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with realistic settings
            browser = await playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process'
                ]
            )
            
            # Create context with cookies
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # New York
                color_scheme='dark',
                accept_downloads=False
            )
            
            # Add cookies to context
            await context.add_cookies(cookie_data['cookies'])
            
            # Store context for later use
            self.active_contexts[username] = {
                'playwright': playwright,
                'browser': browser,
                'context': context,
                'created_at': datetime.now()
            }
            
            log_account(username, "CreateBrowserContext", "SUCCESS", headless=headless)
            log_end("CreateBrowserContext", start, True)
            
            logger.info(f"✅ Browser context created for {username}")
            return context
            
        except Exception as e:
            log_error("CreateBrowserContext", str(e), context={'username': username})
            log_end("CreateBrowserContext", start, False, error=str(e))
            return None
    
    async def close_context(self, username: str):
        """
        Close browser context and clean up
        
        Args:
            username: TikTok username
        """
        start = log_start("CloseBrowserContext", username=username)
        
        if username in self.active_contexts:
            try:
                ctx = self.active_contexts[username]
                
                # Close in order: context -> browser -> playwright
                await ctx['context'].close()
                await ctx['browser'].close()
                await ctx['playwright'].stop()
                
                del self.active_contexts[username]
                
                log_account(username, "CloseBrowserContext", "SUCCESS")
                log_end("CloseBrowserContext", start, True)
                
                logger.info(f"✅ Browser context closed for {username}")
                
            except Exception as e:
                log_error("CloseBrowserContext", str(e), context={'username': username})
                log_end("CloseBrowserContext", start, False, error=str(e))
        else:
            logger.warning(f"⚠️ No active context found for {username}")
            log_end("CloseBrowserContext", start, False, reason="no_context")
    
    async def verify_session(self, username: str) -> bool:
        """
        Verify if cookie session is still valid by checking TikTok
        
        Args:
            username: TikTok username
            
        Returns:
            True if session is valid, False otherwise
        """
        start = log_start("VerifySession", username=username)
        
        context = await self.create_browser_context(username, headless=True)
        if not context:
            log_end("VerifySession", start, False, reason="no_context")
            return False
        
        try:
            page = await context.new_page()
            
            # Navigate to TikTok
            await page.goto('https://www.tiktok.com/', wait_until='networkidle', timeout=30000)
            
            # Wait for page to load
            await page.wait_for_timeout(3000)
            
            # Check if we're logged in by looking for profile elements
            # Multiple selectors as fallback
            logged_in_selectors = [
                'a[href*="/profile"]',
                'button[data-e2e="user-avatar"]',
                'div[data-e2e="profile-icon"]',
                '[data-e2e="nav-profile"]'
            ]
            
            is_valid = False
            for selector in logged_in_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        is_valid = True
                        break
                except:
                    continue
            
            if is_valid:
                logger.info(f"✅ Session valid for {username}")
                log_account(username, "VerifySession", "VALID")
                log_end("VerifySession", start, True)
            else:
                logger.warning(f"⚠️ Session invalid for {username} - needs re-login")
                log_account(username, "VerifySession", "INVALID")
                log_end("VerifySession", start, False, reason="invalid_session")
            
            await page.close()
            return is_valid
            
        except Exception as e:
            log_error("VerifySession", str(e), context={'username': username})
            log_end("VerifySession", start, False, error=str(e))
            return False
        finally:
            await self.close_context(username)
    
    def export_cookies_instructions(self, browser_name: str = 'chrome') -> str:
        """
        Guide for exporting cookies manually from browser
        
        Args:
            browser_name: 'chrome', 'firefox', or 'manual'
            
        Returns:
            Detailed instructions as string
        """
        instructions = {
            'chrome': """
┌─────────────────────────────────────────────────────────────┐
│ 📋 CHROME COOKIE EXPORT INSTRUCTIONS                        │
└─────────────────────────────────────────────────────────────┘

METHOD 1: Using EditThisCookie Extension (RECOMMENDED)
──────────────────────────────────────────────────────

1. Install "EditThisCookie" extension from Chrome Web Store
   https://chrome.google.com/webstore/detail/editthiscookie/

2. Log into TikTok normally in Chrome
   - Go to www.tiktok.com
   - Complete login (including any 2FA)
   - Ensure you're fully logged in

3. Click the EditThisCookie icon in your toolbar

4. Click the "Export" button (download icon at bottom)

5. The cookies will be copied to your clipboard as JSON

6. Create a new file: affilify_data/cookies/USERNAME.json

7. Paste the cookies into the file

8. Format the file as follows:
   {
     "username": "your_username",
     "cookies": [PASTE_COOKIES_HERE],
     "saved_at": "2025-01-07T12:00:00",
     "expires_at": "2025-02-06T12:00:00"
   }

9. Save the file

METHOD 2: Using Browser Developer Tools
────────────────────────────────────────

1. Log into TikTok

2. Press F12 to open Developer Tools

3. Go to "Application" tab

4. In left sidebar, expand "Cookies" → "https://www.tiktok.com"

5. You'll see all cookies - copy the important ones:
   - sessionid
   - sid_tt
   - uid_tt
   - ttwid
   - msToken

6. Format them into JSON as shown above

✅ You're ready once the file is saved!
            """,
            
            'firefox': """
┌─────────────────────────────────────────────────────────────┐
│ 📋 FIREFOX COOKIE EXPORT INSTRUCTIONS                       │
└─────────────────────────────────────────────────────────────┘

METHOD 1: Using Cookie Quick Manager Extension (RECOMMENDED)
─────────────────────────────────────────────────────────────

1. Install "Cookie Quick Manager" from Firefox Add-ons
   https://addons.mozilla.org/firefox/addon/cookie-quick-manager/

2. Log into TikTok normally in Firefox
   - Go to www.tiktok.com
   - Complete login (including any 2FA)

3. Click the Cookie Quick Manager icon

4. Click on "tiktok.com" in the domain list

5. Click "Export" button

6. Save the exported JSON

7. Rename file to: affilify_data/cookies/USERNAME.json

8. Edit the file to add username and dates:
   {
     "username": "your_username",
     "cookies": [EXPORTED_COOKIES],
     "saved_at": "2025-01-07T12:00:00",
     "expires_at": "2025-02-06T12:00:00"
   }

✅ You're ready once the file is saved!
            """,
            
            'manual': """
┌─────────────────────────────────────────────────────────────┐
│ 📋 MANUAL COOKIE EXPORT (ANY BROWSER)                       │
└─────────────────────────────────────────────────────────────┘

USING PYTHON (EASIEST FOR MULTIPLE ACCOUNTS)
─────────────────────────────────────────────

1. Install browser-cookie3:
   pip install browser-cookie3

2. Run this Python script:
```python
import browser_cookie3
import json
from datetime import datetime, timedelta

# Get cookies from Chrome (or firefox, edge, etc.)
cookies = browser_cookie3.chrome(domain_name='tiktok.com')

# Convert to list of dictionaries
cookie_list = []
for cookie in cookies:
    cookie_list.append({
        'name': cookie.name,
        'value': cookie.value,
        'domain': cookie.domain,
        'path': cookie.path,
        'expires': cookie.expires,
        'secure': cookie.secure,
        'httpOnly': getattr(cookie, 'httpOnly', False),
        'sameSite': 'Lax'
    })

# Format for AFFILIFY
username = input("Enter TikTok username: ")
cookie_data = {
    'username': username,
    'cookies': cookie_list,
    'saved_at': datetime.now().isoformat(),
    'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
}

# Save to file
with open(f'affilify_data/cookies/{username}.json', 'w') as f:
    json.dump(cookie_data, f, indent=2)

print(f"✅ Cookies saved for {username}!")
```

3. Run this for each account

✅ Done!
            """
        }
        
        return instructions.get(browser_name, instructions['manual'])
    
    def batch_verify_cookies(self, usernames: List[str]) -> Dict[str, Dict]:
        """
        Verify multiple accounts' cookies in batch
        
        Args:
            usernames: List of TikTok usernames
            
        Returns:
            Dict with username: status info
        """
        start = log_start("BatchVerifyCookies", total_accounts=len(usernames))
        
        results = {}
        
        for username in usernames:
            cookie_file = self.cookies_dir / f"{username}.json"
            
            if cookie_file.exists():
                cookie_data = self.load_cookies(username)
                if cookie_data:
                    expires_at = datetime.fromisoformat(cookie_data['expires_at'])
                    days_remaining = (expires_at - datetime.now()).days
                    
                    if days_remaining > 0:
                        status = 'valid'
                    else:
                        status = 'expired'
                    
                    results[username] = {
                        'status': status,
                        'days_remaining': days_remaining,
                        'file': str(cookie_file)
                    }
                else:
                    results[username] = {
                        'status': 'invalid',
                        'days_remaining': 0,
                        'file': str(cookie_file)
                    }
            else:
                results[username] = {
                    'status': 'missing',
                    'days_remaining': 0,
                    'file': None
                }
        
        # Summary
        valid_count = sum(1 for r in results.values() if r['status'] == 'valid')
        expired_count = sum(1 for r in results.values() if r['status'] == 'expired')
        missing_count = sum(1 for r in results.values() if r['status'] == 'missing')
        
        logger.info(f"📊 Cookie verification complete:")
        logger.info(f"   ✅ Valid: {valid_count}")
        logger.info(f"   ⚠️ Expired: {expired_count}")
        logger.info(f"   ❌ Missing: {missing_count}")
        
        log_end("BatchVerifyCookies", start, True, 
               valid=valid_count,
               expired=expired_count,
               missing=missing_count)
        
        return results
    
    def get_active_contexts_count(self) -> int:
        """
        Get number of currently active browser contexts
        
        Returns:
            Count of active contexts
        """
        return len(self.active_contexts)
    
    async def cleanup_stale_contexts(self, max_age_minutes: int = 30):
        """
        Close contexts that have been open too long
        
        Args:
            max_age_minutes: Maximum age in minutes before closing
        """
        start = log_start("CleanupStaleContexts", max_age=max_age_minutes)
        
        stale_usernames = []
        now = datetime.now()
        
        for username, ctx_data in self.active_contexts.items():
            age = (now - ctx_data['created_at']).total_seconds() / 60
            if age > max_age_minutes:
                stale_usernames.append(username)
        
        for username in stale_usernames:
            logger.info(f"🧹 Closing stale context for {username}")
            await self.close_context(username)
        
        log_end("CleanupStaleContexts", start, True, cleaned=len(stale_usernames))
        
        logger.info(f"✅ Cleaned up {len(stale_usernames)} stale contexts")


# Demo and testing
async def demo_cookie_manager():
    """
    Demo of how to use Cookie Manager
    """
    print("\n" + "="*70)
    print("🍪 AFFILIFY COOKIE MANAGER - DEMONSTRATION")
    print("="*70)
    
    manager = CookieManager()
    
    # Show export instructions
    print("\n" + "="*70)
    print("STEP 1: EXPORT COOKIES FROM YOUR BROWSER")
    print("="*70)
    print(manager.export_cookies_instructions('chrome'))
    
    # Check if any cookies exist
    print("\n" + "="*70)
    print("STEP 2: VERIFY EXISTING COOKIES")
    print("="*70)
    
    # Example usernames (replace with your actual accounts)
    test_usernames = [f"tiktoker_{i:03d}" for i in range(1, 31)]
    
    results = manager.batch_verify_cookies(test_usernames)
    
    # Display results
    print("\n📊 COOKIE STATUS:")
    for username, result in results.items():
        status = result['status']
        if status == 'valid':
            icon = "✅"
            days = result['days_remaining']
            info = f"Valid ({days} days remaining)"
        elif status == 'expired':
            icon = "⚠️"
            info = "EXPIRED - Re-export needed"
        else:
            icon = "❌"
            info = "MISSING - Export cookies"
        
        print(f"{icon} {username:<20} {info}")
    
    # Test verification (only if cookies exist)
    cookie_file = Path("affilify_data/cookies/tiktoker_001.json")
    if cookie_file.exists():
        print("\n" + "="*70)
        print("STEP 3: TEST SESSION VERIFICATION")
        print("="*70)
        
        is_valid = await manager.verify_session("tiktoker_001")
        if is_valid:
            print("✅ Session verification successful!")
        else:
            print("❌ Session verification failed - cookies may be invalid")
    else:
        print("\n⚠️ No cookies found for testing")
        print("   Please export cookies first using the instructions above")
    
    print("\n" + "="*70)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Export cookies for all 30 accounts")
    print("2. Verify all cookies are valid")
    print("3. Start the main system!")
    print("\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_cookie_manager())
