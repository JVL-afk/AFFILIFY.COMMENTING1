#!/usr/bin/env python3.11
"""
SIMPLE LIVE COMMENT POSTING WITH SCREENSHOTS
Direct approach - no complex automation, just post and screenshot!
"""

import asyncio
import os
import json
from playwright.async_api import async_playwright
from pathlib import Path

async def post_comment_simple():
    print("=" * 80)
    print("🚀 SIMPLE LIVE COMMENT POSTING - INVESTOR PROOF")
    print("=" * 80)
    
    # Test videos (real TikTok video IDs we discovered)
    test_videos = [
        {
            'video_id': '7595704503194635551',
            'comment': "Great content! For anyone looking to automate their affiliate marketing, affilify.eu is worth checking out 👍"
        },
        {
            'video_id': '7602521785145363743',
            'comment': "This is exactly what I needed! 🔥 Been using affilify.eu to automate my affiliate sites and it's a game changer!"
        },
        {
            'video_id': '7303149977247747370',
            'comment': "Love this! 💯 Just started using affilify.eu for my side hustle and already seeing results!"
        }
    ]
    
    # Load cookies
    cookie_file = "/home/ubuntu/AFFILIFY.COMMENTING1/affilify_data/cookies/TIKTOK1.json"
    
    print(f"\n📂 Loading cookies from: {cookie_file}")
    
    with open(cookie_file, 'r') as f:
        cookie_data = json.load(f)
    
    # Extract cookies array from the JSON structure
    if isinstance(cookie_data, dict) and 'cookies' in cookie_data:
        cookies = cookie_data['cookies']
    else:
        cookies = cookie_data
    
    # Fix cookie attributes for Playwright
    for cookie in cookies:
        # Fix sameSite
        if 'sameSite' in cookie:
            if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                cookie['sameSite'] = 'Lax'
        else:
            cookie['sameSite'] = 'Lax'
        
        # Fix expires to be float
        if 'expires' in cookie and not isinstance(cookie['expires'], (int, float)):
            try:
                cookie['expires'] = float(cookie['expires'])
            except:
                del cookie['expires']
    
    print(f"✅ Loaded {len(cookies)} cookies")
    
    # Create screenshots directory
    screenshot_dir = Path("/home/ubuntu/AFFILIFY.COMMENTING1/investor_screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    
    print(f"\n📸 Screenshots will be saved to: {screenshot_dir}")
    
    async with async_playwright() as p:
        print(f"\n🌐 Launching browser...")
        
        browser = await p.chromium.launch(
            headless=False,  # Non-headless for better success
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Add cookies
        await context.add_cookies(cookies)
        print(f"✅ Cookies injected")
        
        page = await context.new_page()
        
        results = []
        
        for i, video in enumerate(test_videos, 1):
            print(f"\n{'='*80}")
            print(f"POSTING COMMENT {i}/{len(test_videos)}")
            print(f"{'='*80}")
            
            video_url = f"https://www.tiktok.com/@unknown/video/{video['video_id']}"
            
            print(f"   Video ID: {video['video_id']}")
            print(f"   URL: {video_url}")
            print(f"   Comment: \"{video['comment'][:60]}...\"")
            
            try:
                print(f"\n   🔄 Navigating to video...")
                await page.goto(video_url, wait_until='networkidle', timeout=30000)
                
                # Wait a bit for page to load
                await asyncio.sleep(3)
                
                # Take screenshot of video page
                screenshot_path = screenshot_dir / f"video_{i}_page.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"   📸 Screenshot saved: {screenshot_path.name}")
                
                # Try to find comment box
                print(f"\n   💬 Looking for comment box...")
                
                # Multiple selectors to try
                comment_selectors = [
                    'div[data-e2e="comment-input"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="comment"]',
                    'div.public-DraftEditor-content'
                ]
                
                comment_box = None
                for selector in comment_selectors:
                    try:
                        comment_box = await page.wait_for_selector(selector, timeout=5000)
                        if comment_box:
                            print(f"   ✅ Found comment box with selector: {selector}")
                            break
                    except:
                        continue
                
                if not comment_box:
                    print(f"   ⚠️ Could not find comment box, taking screenshot anyway...")
                    screenshot_path = screenshot_dir / f"video_{i}_no_comment_box.png"
                    await page.screenshot(path=str(screenshot_path), full_page=True)
                    results.append({
                        'video_id': video['video_id'],
                        'success': False,
                        'error': 'Comment box not found',
                        'screenshot': str(screenshot_path)
                    })
                    continue
                
                # Click comment box
                await comment_box.click()
                await asyncio.sleep(1)
                
                # Type comment
                print(f"   ⌨️  Typing comment...")
                await comment_box.fill(video['comment'])
                await asyncio.sleep(2)
                
                # Take screenshot of comment typed
                screenshot_path = screenshot_dir / f"video_{i}_comment_typed.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"   📸 Screenshot saved: {screenshot_path.name}")
                
                # Try to find post button
                print(f"\n   🔍 Looking for post button...")
                
                post_selectors = [
                    'div[data-e2e="comment-post"]',
                    'button:has-text("Post")',
                    'div:has-text("Post")',
                    'button[type="submit"]'
                ]
                
                post_button = None
                for selector in post_selectors:
                    try:
                        post_button = await page.wait_for_selector(selector, timeout=3000)
                        if post_button:
                            print(f"   ✅ Found post button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not post_button:
                    print(f"   ⚠️ Could not find post button")
                    print(f"   📸 But we have screenshot of comment typed!")
                    results.append({
                        'video_id': video['video_id'],
                        'success': 'partial',
                        'message': 'Comment typed but not posted',
                        'screenshot': str(screenshot_path)
                    })
                    continue
                
                # Click post button
                print(f"   🚀 Clicking post button...")
                await post_button.click()
                await asyncio.sleep(3)
                
                # Take screenshot after posting
                screenshot_path = screenshot_dir / f"video_{i}_posted.png"
                await page.screenshot(path=str(screenshot_path), full_page=False)
                print(f"   📸 Screenshot saved: {screenshot_path.name}")
                
                print(f"\n   ✅ COMMENT POSTED SUCCESSFULLY!")
                
                results.append({
                    'video_id': video['video_id'],
                    'success': True,
                    'message': 'Comment posted',
                    'screenshot': str(screenshot_path)
                })
                
                # Wait before next post
                if i < len(test_videos):
                    print(f"\n   ⏳ Waiting 30 seconds before next post...")
                    await asyncio.sleep(30)
                
            except Exception as e:
                print(f"\n   ❌ ERROR: {e}")
                screenshot_path = screenshot_dir / f"video_{i}_error.png"
                try:
                    await page.screenshot(path=str(screenshot_path))
                    print(f"   📸 Error screenshot saved: {screenshot_path.name}")
                except:
                    pass
                
                results.append({
                    'video_id': video['video_id'],
                    'success': False,
                    'error': str(e),
                    'screenshot': str(screenshot_path) if screenshot_path.exists() else None
                })
        
        await browser.close()
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 FINAL RESULTS")
    print(f"{'='*80}")
    
    successful = sum(1 for r in results if r['success'] == True)
    partial = sum(1 for r in results if r['success'] == 'partial')
    failed = len(results) - successful - partial
    
    print(f"\n✅ Successfully posted: {successful}/{len(results)}")
    print(f"⚠️ Partially completed: {partial}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    print(f"\n📸 SCREENSHOTS FOR INVESTORS:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Video {result['video_id']}")
        if result.get('screenshot'):
            print(f"   Screenshot: {result['screenshot']}")
        print(f"   Status: {result.get('message', result.get('error', 'Unknown'))}")
    
    print(f"\n{'='*80}")
    print("🎉 INVESTOR PROOF READY!")
    print(f"{'='*80}")
    print(f"\nAll screenshots saved to: {screenshot_dir}")
    
    return results

if __name__ == "__main__":
    asyncio.run(post_comment_simple())
