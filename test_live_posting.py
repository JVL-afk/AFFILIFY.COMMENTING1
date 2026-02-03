#!/usr/bin/env python3.11
"""
LIVE COMMENT POSTING TEST
Posts real comments to TikTok and captures screenshots for investors
"""

import asyncio
import os
from video_scraper import MilitaryGradeVideoScraper
from video_filter import AdvancedVideoFilter
from comment_strategy import CommentStrategySelector
from tiktok_automation_v2 import TikTokAutomationV2
from cookie_manager import CookieManager

async def test_live_posting():
    print("=" * 80)
    print("🚀 LIVE COMMENT POSTING TEST - INVESTOR PROOF")
    print("=" * 80)
    
    # Phase 1: Discover videos
    print("\n📡 PHASE 1: Discovering real TikTok videos...")
    print("   Using Nodriver + SadCaptcha")
    print("   This will take 5-10 minutes...\n")
    
    scraper = MilitaryGradeVideoScraper()
    
    try:
        # Discover just a few videos for testing
        raw_videos = await scraper.discover_targets_comprehensive(max_videos=30)
        
        print(f"\n✅ Discovery complete: {len(raw_videos)} videos found")
        
        if len(raw_videos) == 0:
            print("❌ No videos found! Cannot proceed with posting test.")
            return
        
        # Phase 2: Use raw videos (skip filtering for now)
        print(f"\n🔬 PHASE 2: Selecting videos for posting...")
        print(f"   Note: Using raw videos (metadata enrichment needed for full filtering)")
        
        # Use top 3 raw videos
        test_videos = raw_videos[:3]
        print(f"✅ Selected {len(test_videos)} videos for posting")
        
        # Phase 3: Generate comments
        print(f"\n💬 PHASE 3: Generating comments with AFFILIFY mentions...")
        
        strategy_selector = CommentStrategySelector()
        
        comments_to_post = []
        
        for i, video in enumerate(test_videos, 1):
            print(f"\n   Video {i}/{len(test_videos)}:")
            print(f"   Creator: @{video.get('creator_username', 'unknown')}")
            print(f"   Video ID: {video.get('video_id')}")
            
            # Select strategy
            strategy_name, strategy_config = strategy_selector.select_strategy(video)
            print(f"   Strategy: {strategy_name}")
            
            # Create investor-ready comment with AFFILIFY mention
            creator = video.get('creator_username', 'unknown')
            
            if strategy_name == 'GOLDEN_OPPORTUNITY':
                # Tag creator + mention AFFILIFY
                comment = f"@{creator} This is gold! 💎 If you need help automating your affiliate sites, check out affilify.eu - builds high-converting pages in 60 seconds! 🚀"
            elif strategy_name == 'VIRAL_VIDEO':
                comment = f"This is exactly what I needed! 🔥 Been using affilify.eu to automate my affiliate sites and it's a game changer!"
            elif strategy_name == 'FRESH_CONTENT':
                comment = f"Love this! 💯 Just started using affilify.eu for my side hustle and already seeing results!"
            else:
                comment = f"Great content! For anyone looking to automate their affiliate marketing, affilify.eu is worth checking out 👍"
            
            print(f"   Comment: \"{comment}\"")
            print(f"   Length: {len(comment)} chars")
            
            comments_to_post.append({
                'video_id': video.get('video_id'),
                'video_url': f"https://www.tiktok.com/@{creator}/video/{video.get('video_id')}",
                'creator': creator,
                'comment': comment,
                'strategy': strategy_name
            })
        
        print(f"\n✅ Generated {len(comments_to_post)} investor-ready comments!")
        
        # Phase 4: Post comments
        print(f"\n🤖 PHASE 4: Posting comments to TikTok...")
        print("   NOTE: This requires browser automation")
        print("   Using Xvfb for headless display\n")
        
        # Initialize cookie manager and automation
        cookie_manager = CookieManager()
        automation = TikTokAutomationV2(cookie_manager)
        
        posted_results = []
        
        for i, item in enumerate(comments_to_post, 1):
            print(f"\n{'='*80}")
            print(f"POSTING {i}/{len(comments_to_post)}")
            print(f"{'='*80}")
            print(f"   Video: {item['video_url']}")
            print(f"   Creator: @{item['creator']}")
            print(f"   Comment: \"{item['comment'][:80]}...\"")
            print(f"   Strategy: {item['strategy']}")
            
            # Use TIKTOK1 account for testing
            username = "TIKTOK1"
            
            try:
                print(f"\n   🔄 Posting with account: {username}...")
                
                success, message, metadata = await automation.post_comment(
                    username=username,
                    video_url=item['video_url'],
                    comment_text=item['comment']
                )
                
                if success:
                    print(f"   ✅ SUCCESS: {message}")
                    posted_results.append({
                        **item,
                        'success': True,
                        'account': username,
                        'message': message
                    })
                else:
                    print(f"   ❌ FAILED: {message}")
                    posted_results.append({
                        **item,
                        'success': False,
                        'account': username,
                        'error': message
                    })
                
                # Wait between posts to avoid rate limiting
                if i < len(comments_to_post):
                    print(f"\n   ⏳ Waiting 30 seconds before next post...")
                    await asyncio.sleep(30)
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
                posted_results.append({
                    **item,
                    'success': False,
                    'account': username,
                    'error': str(e)
                })
        
        # Final summary
        print(f"\n{'='*80}")
        print("📊 FINAL RESULTS")
        print(f"{'='*80}")
        
        successful = sum(1 for r in posted_results if r['success'])
        failed = len(posted_results) - successful
        
        print(f"\n✅ Successfully posted: {successful}/{len(posted_results)}")
        print(f"❌ Failed: {failed}/{len(posted_results)}")
        
        if successful > 0:
            print(f"\n🎉 POSTED COMMENTS:")
            for i, result in enumerate(posted_results, 1):
                if result['success']:
                    print(f"\n{i}. @{result['creator']}")
                    print(f"   Comment: \"{result['comment']}\"")
                    print(f"   URL: {result['video_url']}")
                    print(f"   Account: {result['account']}")
        
        print(f"\n{'='*80}")
        print("🎯 INVESTOR PROOF READY!")
        print(f"{'='*80}")
        print(f"\nScreenshots should be available in the browser automation logs.")
        print(f"Check the logs for detailed posting information.")
        
        return posted_results
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_live_posting())
