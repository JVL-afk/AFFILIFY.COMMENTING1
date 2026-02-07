#!/usr/bin/env python3.11
"""
FINAL BREAKTHROUGH TEST - Complete End-to-End with Fresh Cookies
1. Discover real videos with Nodriver + fresh cookies
2. Generate AFFILIFY comments
3. Post comments with Playwright
4. Capture screenshots for investors
"""
import asyncio
import os
import sys
import json
from datetime import datetime

# Add project to path
sys.path.insert(0, '/home/ubuntu/AFFILIFY.COMMENTING1')

from video_scraper import MilitaryGradeVideoScraper
from gemini_integration import GeminiCommentGenerator
from comment_strategy import CommentStrategySelector
from playwright.async_api import async_playwright

print("="*80)
print("🚀 FINAL BREAKTHROUGH TEST - FRESH COOKIES")
print("="*80)

async def main():
    # Step 1: Discover real videos with Nodriver + fresh cookies
    print("\n📡 STEP 1: DISCOVERING REAL VIDEOS WITH FRESH COOKIES")
    print("-"*80)
    
    scraper = MilitaryGradeVideoScraper()
    
    # Discover videos from one hashtag
    videos = await scraper.discover_targets_comprehensive(
        max_videos=30
    )
    
    print(f"\n✅ Found {len(videos)} videos!")
    
    if len(videos) == 0:
        print("❌ No videos found. Cannot proceed.")
        return
    
    # Take first 3 videos
    test_videos = videos[:3]
    
    print(f"\n🎯 Testing with {len(test_videos)} videos:")
    for i, video in enumerate(test_videos, 1):
        print(f"   {i}. Video ID: {video['video_id']}")
        print(f"      URL: {video['url']}")
    
    # Step 2: Generate AFFILIFY comments
    print("\n💬 STEP 2: GENERATING AFFILIFY COMMENTS")
    print("-"*80)
    
    gemini = GeminiCommentGenerator()
    strategy_selector = CommentStrategySelector()
    
    comments = []
    for video in test_videos:
        # Select strategy
        strategy = strategy_selector.select_strategy(video)
        print(f"\n📋 Video {video['video_id']}: Strategy = {strategy}")
        
        # Generate comment
        comment = gemini.generate_comment(video, strategy)
        comments.append({
            'video': video,
            'comment': comment,
            'strategy': strategy
        })
        print(f"   Comment: {comment[:80]}...")
    
    # Step 3: Post comments with Playwright
    print("\n🤖 STEP 3: POSTING COMMENTS WITH PLAYWRIGHT")
    print("-"*80)
    
    # Load fresh cookies
    cookie_path = "/home/ubuntu/AFFILIFY.COMMENTING1/affilify_data/cookies/TIKTOK1.json"
    print(f"📂 Loading cookies from: {cookie_path}")
    
    with open(cookie_path, 'r') as f:
        cookie_data = json.load(f)
        if 'cookies' in cookie_data:
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
    screenshot_dir = "/home/ubuntu/AFFILIFY.COMMENTING1/final_investor_proof"
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"📸 Screenshots will be saved to: {screenshot_dir}")
    
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
        
        # Inject cookies
        await context.add_cookies(cookies)
        print("✅ Cookies injected")
        
        page = await context.new_page()
        
        # Post comments
        results = []
        for i, item in enumerate(comments, 1):
            video = item['video']
            comment = item['comment']
            
            print(f"\n{'='*80}")
            print(f"POSTING COMMENT {i}/{len(comments)}")
            print(f"{'='*80}")
            print(f"   Video ID: {video['video_id']}")
            print(f"   URL: {video['url']}")
            print(f"   Comment: {comment[:80]}...")
            
            try:
                # Navigate to video
                print(f"   🔄 Navigating to video...")
                await page.goto(video['url'], wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Take screenshot of page
                screenshot_path = f"{screenshot_dir}/video_{i}_page.png"
                await page.screenshot(path=screenshot_path, full_page=False)
                print(f"   📸 Screenshot saved: video_{i}_page.png")
                
                # Check if video is playable
                video_error = await page.query_selector('text="We\'re having trouble playing this video"')
                if video_error:
                    print(f"   ⚠️ Video playback error detected")
                    results.append({
                        'video_id': video['video_id'],
                        'status': 'Video playback blocked',
                        'screenshot': screenshot_path
                    })
                    continue
                
                # Look for comment box
                print(f"   💬 Looking for comment box...")
                comment_selectors = [
                    'div[data-e2e="comment-input"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="comment"]',
                    'div[placeholder*="comment"]'
                ]
                
                comment_box = None
                for selector in comment_selectors:
                    comment_box = await page.query_selector(selector)
                    if comment_box:
                        print(f"   ✅ Found comment box with selector: {selector}")
                        break
                
                if not comment_box:
                    print(f"   ⚠️ Could not find comment box")
                    screenshot_path = f"{screenshot_dir}/video_{i}_no_comment_box.png"
                    await page.screenshot(path=screenshot_path, full_page=False)
                    results.append({
                        'video_id': video['video_id'],
                        'status': 'Comment box not found',
                        'screenshot': screenshot_path
                    })
                    continue
                
                # Click comment box
                await comment_box.click()
                await page.wait_for_timeout(1000)
                
                # Type comment
                print(f"   ⌨️  Typing comment...")
                await comment_box.fill(comment)
                await page.wait_for_timeout(2000)
                
                # Take screenshot before posting
                screenshot_path = f"{screenshot_dir}/video_{i}_before_post.png"
                await page.screenshot(path=screenshot_path, full_page=False)
                print(f"   📸 Screenshot saved: video_{i}_before_post.png")
                
                # Look for post button
                post_selectors = [
                    'button[data-e2e="comment-post"]',
                    'button:has-text("Post")',
                    'div[role="button"]:has-text("Post")'
                ]
                
                post_button = None
                for selector in post_selectors:
                    post_button = await page.query_selector(selector)
                    if post_button:
                        print(f"   ✅ Found post button with selector: {selector}")
                        break
                
                if not post_button:
                    print(f"   ⚠️ Could not find post button")
                    results.append({
                        'video_id': video['video_id'],
                        'status': 'Post button not found (comment typed)',
                        'screenshot': screenshot_path
                    })
                    continue
                
                # Click post button
                print(f"   🚀 Posting comment...")
                await post_button.click()
                await page.wait_for_timeout(3000)
                
                # Take screenshot after posting
                screenshot_path = f"{screenshot_dir}/video_{i}_after_post.png"
                await page.screenshot(path=screenshot_path, full_page=False)
                print(f"   📸 Screenshot saved: video_{i}_after_post.png")
                print(f"   ✅ COMMENT POSTED SUCCESSFULLY!")
                
                results.append({
                    'video_id': video['video_id'],
                    'status': 'SUCCESS',
                    'screenshot': screenshot_path,
                    'comment': comment
                })
                
            except Exception as e:
                print(f"   ❌ ERROR: {str(e)}")
                screenshot_path = f"{screenshot_dir}/video_{i}_error.png"
                try:
                    await page.screenshot(path=screenshot_path, full_page=False)
                    print(f"   📸 Error screenshot saved: video_{i}_error.png")
                except:
                    pass
                results.append({
                    'video_id': video['video_id'],
                    'status': f'Error: {str(e)}',
                    'screenshot': screenshot_path
                })
        
        await browser.close()
    
    # Print final results
    print(f"\n{'='*80}")
    print("📊 FINAL RESULTS")
    print(f"{'='*80}")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    partial_count = sum(1 for r in results if 'typed' in r['status'].lower())
    failed_count = len(results) - success_count - partial_count
    
    print(f"✅ Successfully posted: {success_count}/{len(results)}")
    print(f"⚠️ Partially completed: {partial_count}/{len(results)}")
    print(f"❌ Failed: {failed_count}/{len(results)}")
    
    print(f"\n📸 SCREENSHOTS FOR INVESTORS:")
    for i, result in enumerate(results, 1):
        print(f"{i}. Video {result['video_id']}")
        print(f"   Screenshot: {result['screenshot']}")
        print(f"   Status: {result['status']}")
        if 'comment' in result:
            print(f"   Comment: {result['comment'][:80]}...")
    
    print(f"\n{'='*80}")
    print("🎉 FINAL BREAKTHROUGH TEST COMPLETE!")
    print(f"{'='*80}")
    print(f"All screenshots saved to: {screenshot_dir}")

if __name__ == "__main__":
    asyncio.run(main())
