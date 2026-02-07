#!/usr/bin/env python3.11
"""
Simple test: Post ONE comment to demonstrate the system works
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright

# Test with a KNOWN good TikTok video URL
TEST_VIDEO_URL = "https://www.tiktok.com/@affiliatelab/video/7434758906717064481"
TEST_COMMENT = "This is gold! 💎 Check out affilify.eu for automating your affiliate sites - builds high-converting pages in 60 seconds! 🚀"

async def main():
    print("="*80)
    print("🚀 SIMPLE COMMENT POSTING TEST")
    print("="*80)
    
    # Load fresh cookies
    cookie_path = "/home/ubuntu/AFFILIFY.COMMENTING1/affilify_data/cookies/TIKTOK1.json"
    print(f"\n📂 Loading cookies from: {cookie_path}")
    
    with open(cookie_path, 'r') as f:
        cookie_data = json.load(f)
        if 'cookies' in cookie_data:
            cookies = cookie_data['cookies']
        else:
            cookies = cookie_data
    
    # Fix cookie attributes
    for cookie in cookies:
        if 'sameSite' in cookie:
            if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
        else:
            cookie['sameSite'] = 'Lax'
        
        if 'expires' in cookie and not isinstance(cookie['expires'], (int, float)):
            try:
                cookie['expires'] = float(cookie['expires'])
            except:
                del cookie['expires']
    
    print(f"✅ Loaded {len(cookies)} cookies")
    
    # Create screenshots directory
    screenshot_dir = "/home/ubuntu/AFFILIFY.COMMENTING1/simple_test_proof"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # Launch Playwright
    async with async_playwright() as p:
        print("\n🌐 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        await context.add_cookies(cookies)
        print("✅ Cookies injected")
        
        page = await context.new_page()
        
        print(f"\n🔄 Navigating to: {TEST_VIDEO_URL}")
        await page.goto(TEST_VIDEO_URL, wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Take initial screenshot
        await page.screenshot(path=f"{screenshot_dir}/01_page_loaded.png", full_page=False)
        print(f"📸 Screenshot 1: Page loaded")
        
        # Check for video error
        try:
            video_error = await page.query_selector('text="We\'re having trouble"')
            if video_error:
                print("⚠️ Video playback error detected")
                await page.screenshot(path=f"{screenshot_dir}/02_video_error.png", full_page=False)
                print("❌ Cannot proceed - video blocked")
                await browser.close()
                return
        except:
            pass
        
        print("\n💬 Looking for comment box...")
        
        # Try multiple selectors
        comment_box = None
        selectors = [
            'div[data-e2e="comment-input"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="omment"]',
            'div[placeholder*="omment"]'
        ]
        
        for selector in selectors:
            try:
                comment_box = await page.query_selector(selector)
                if comment_box:
                    print(f"✅ Found comment box: {selector}")
                    break
            except:
                continue
        
        if not comment_box:
            print("⚠️ Comment box not found, taking screenshot...")
            await page.screenshot(path=f"{screenshot_dir}/02_no_comment_box.png", full_page=False)
            print("❌ Cannot proceed - comment box not found")
            await browser.close()
            return
        
        # Click and type
        print(f"\n⌨️  Typing comment: {TEST_COMMENT[:50]}...")
        await comment_box.click()
        await page.wait_for_timeout(1000)
        await comment_box.fill(TEST_COMMENT)
        await page.wait_for_timeout(2000)
        
        # Screenshot with comment typed
        await page.screenshot(path=f"{screenshot_dir}/03_comment_typed.png", full_page=False)
        print(f"📸 Screenshot 2: Comment typed")
        
        # Look for post button
        print("\n🔍 Looking for post button...")
        post_button = None
        post_selectors = [
            'button[data-e2e="comment-post"]',
            'button:has-text("Post")',
            'div[role="button"]:has-text("Post")'
        ]
        
        for selector in post_selectors:
            try:
                post_button = await page.query_selector(selector)
                if post_button:
                    print(f"✅ Found post button: {selector}")
                    break
            except:
                continue
        
        if not post_button:
            print("⚠️ Post button not found")
            await page.screenshot(path=f"{screenshot_dir}/04_no_post_button.png", full_page=False)
            print("⚠️ Comment typed but cannot post")
            await browser.close()
            return
        
        # Post the comment!
        print("\n🚀 POSTING COMMENT...")
        await post_button.click()
        await page.wait_for_timeout(5000)
        
        # Screenshot after posting
        await page.screenshot(path=f"{screenshot_dir}/05_after_post.png", full_page=False)
        print(f"📸 Screenshot 3: After posting")
        
        # Check if comment appears
        print("\n🔍 Checking if comment was posted...")
        await page.wait_for_timeout(3000)
        
        # Scroll to comments section
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
        except:
            pass
        
        # Final screenshot
        await page.screenshot(path=f"{screenshot_dir}/06_final_view.png", full_page=False)
        print(f"📸 Screenshot 4: Final view")
        
        print("\n" + "="*80)
        print("✅ TEST COMPLETE!")
        print("="*80)
        print(f"Screenshots saved to: {screenshot_dir}")
        print("\nCheck the screenshots to verify if comment was posted!")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
